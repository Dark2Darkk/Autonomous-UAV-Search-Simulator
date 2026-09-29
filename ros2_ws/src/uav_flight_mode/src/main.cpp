#include "uav_flight_mode/mode.hpp"

#include <px4_ros2/components/node_with_mode.hpp>
#include <rclcpp/rclcpp.hpp>


using UavFlightNode =
    px4_ros2::NodeWithModeExecutor<
        UavExecutor,
        Nav2FlightMode
    >;


int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);

    rclcpp::spin(
        std::make_shared<UavFlightNode>(
            "uav_flight_mode",
            true
        )
    );

    rclcpp::shutdown();

    return 0;
}