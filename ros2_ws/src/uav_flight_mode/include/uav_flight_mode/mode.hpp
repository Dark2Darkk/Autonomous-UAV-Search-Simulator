#pragma once

#include <cmath>
#include <memory>

#include <Eigen/Core>

#include <geometry_msgs/msg/twist.hpp>
#include <px4_msgs/msg/vehicle_local_position.hpp>

#include <px4_ros2/components/mode.hpp>
#include <px4_ros2/components/mode_executor.hpp>
#include <px4_ros2/control/setpoint_types/experimental/trajectory.hpp>

#include <rclcpp/rclcpp.hpp>


class Nav2FlightMode : public px4_ros2::ModeBase
{
public:
    explicit Nav2FlightMode(rclcpp::Node& node)
        : ModeBase(
            node,
            px4_ros2::ModeBase::Settings{"Nav2 Flight Mode"}
        )
    {
        trajectory_setpoint_ =
            std::make_shared<px4_ros2::TrajectorySetpointType>(*this);

        // Nav2 velocity commands
        cmd_vel_sub_ =
            node.create_subscription<geometry_msgs::msg::Twist>(
                "/cmd_vel",
                10,
                [this](const geometry_msgs::msg::Twist::SharedPtr msg)
                {
                    forward_velocity_ = msg->linear.x;
                    yaw_rate_ = msg->angular.z;

                    last_cmd_time_ = this->node().get_clock()->now();
                    have_cmd_ = true;
                });

        // PX4 heading so body-forward Nav2 velocity can be converted
        // into North/East velocity.
        rclcpp::QoS px4_qos(rclcpp::KeepLast(1));
        px4_qos.best_effort();
        px4_qos.transient_local();

        local_position_sub_ =
            node.create_subscription<px4_msgs::msg::VehicleLocalPosition>(
                "/fmu/out/vehicle_local_position_v1",
                px4_qos,
                [this](const px4_msgs::msg::VehicleLocalPosition::SharedPtr msg)
                {
                    heading_ = msg->heading;
                    heading_valid_ = msg->heading_good_for_control;
                });
    }

    void onActivate() override
    {
        RCLCPP_INFO(
            node().get_logger(),
            "Nav2 flight mode ACTIVE"
        );
    }

    void onDeactivate() override
    {
        RCLCPP_INFO(
            node().get_logger(),
            "Nav2 flight mode DEACTIVATED"
        );
    }

    void updateSetpoint(float dt_s) override
    {
        (void)dt_s;

        float forward = 0.0f;
        float ros_yaw_rate = 0.0f;

        // Stop if Nav2 stops publishing commands.
        if (have_cmd_)
        {
            const double age =
                (node().get_clock()->now() - last_cmd_time_).seconds();

            if (age <= 0.5)
            {
                forward = static_cast<float>(forward_velocity_);
                ros_yaw_rate = static_cast<float>(yaw_rate_);
            }
        }

        float velocity_north = 0.0f;
        float velocity_east = 0.0f;

        if (heading_valid_)
        {
            velocity_north =
                forward * std::cos(heading_);

            velocity_east =
                forward * std::sin(heading_);
        }

        px4_ros2::TrajectorySetpoint setpoint;

        setpoint
            .withHorizontalVelocity(
                Eigen::Vector2f(
                    velocity_north,
                    velocity_east
                )
            )

            // PX4 uses NED:
            // negative Z = above takeoff origin.
            .withPositionZ(-3.0f)

            // ROS yaw rate and NED yaw rate have opposite signs.
            .withYawRate(-ros_yaw_rate);

        trajectory_setpoint_->update(setpoint);
    }

private:
    std::shared_ptr<px4_ros2::TrajectorySetpointType>
        trajectory_setpoint_;

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr
        cmd_vel_sub_;

    rclcpp::Subscription<
        px4_msgs::msg::VehicleLocalPosition
    >::SharedPtr local_position_sub_;

    double forward_velocity_{0.0};
    double yaw_rate_{0.0};

    float heading_{0.0f};
    bool heading_valid_{false};

    bool have_cmd_{false};
    rclcpp::Time last_cmd_time_{0, 0, RCL_ROS_TIME};
};


class UavExecutor : public px4_ros2::ModeExecutorBase
{
public:
    explicit UavExecutor(px4_ros2::ModeBase& owned_mode)
        : ModeExecutorBase(
              px4_ros2::ModeExecutorBase::Settings{}.activate(
                  px4_ros2::ModeExecutorBase::Settings::
                      Activation::ActivateImmediately
              ),
              owned_mode
          ),
          node_(owned_mode.node())
    {
    }

    void onActivate() override
    {
        RCLCPP_INFO(
            node_.get_logger(),
            "UAV executor activated"
        );

        startMission();
    }

    void onDeactivate(DeactivateReason reason) override
    {
        (void)reason;

        RCLCPP_WARN(
            node_.get_logger(),
            "UAV executor deactivated"
        );
    }

private:
    void startMission()
    {
        RCLCPP_INFO(
            node_.get_logger(),
            "Waiting for PX4 preflight checks..."
        );

        waitReadyToArm(
            [this](px4_ros2::Result result)
            {
                if (result != px4_ros2::Result::Success)
                {
                    RCLCPP_ERROR(
                        node_.get_logger(),
                        "PX4 was not ready to arm"
                    );
                    return;
                }

                armVehicle();
            }
        );
    }


    void armVehicle()
    {
        RCLCPP_INFO(
            node_.get_logger(),
            "Arming..."
        );

        arm(
            [this](px4_ros2::Result result)
            {
                if (result != px4_ros2::Result::Success)
                {
                    RCLCPP_ERROR(
                        node_.get_logger(),
                        "Arming failed"
                    );
                    return;
                }

                RCLCPP_INFO(
                    node_.get_logger(),
                    "Armed"
                );

                takeoffVehicle();
            }
        );
    }


    void takeoffVehicle()
    {
        RCLCPP_INFO(
            node_.get_logger(),
            "Taking off..."
        );

        // No altitude passed here because PX4's takeoff()
        // altitude parameter is AMSL, not "meters above spawn".
        takeoff(
            [this](px4_ros2::Result result)
            {
                if (result != px4_ros2::Result::Success)
                {
                    RCLCPP_ERROR(
                        node_.get_logger(),
                        "Takeoff failed"
                    );
                    return;
                }

                RCLCPP_INFO(
                    node_.get_logger(),
                    "Takeoff complete - activating Nav2 mode"
                );

                activateNav2Mode();
            }
        );
    }


    void activateNav2Mode()
    {
        scheduleMode(
            ownedMode().id(),
            [this](px4_ros2::Result result)
            {
                RCLCPP_WARN(
                    node_.get_logger(),
                    "Nav2 flight mode ended with result %d",
                    static_cast<int>(result)
                );
            }
        );
    }

    rclcpp::Node& node_;
};