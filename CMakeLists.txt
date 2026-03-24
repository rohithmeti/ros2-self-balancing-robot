cmake_minimum_required(VERSION 3.8)
project(ros2_twsbr2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

# =========================================================
# INSTALL SCRIPTS (Add all your python files here)
# =========================================================
install(PROGRAMS
  ros2_twsbr2/self_balance_controller.py
  ros2_twsbr2/check_motors.py
  ros2_twsbr2/test_turn.py
  ros2_twsbr2/wasdcon.py
  ros2_twsbr2/wasd_driver.py
  DESTINATION lib/${PROJECT_NAME}
)
# =========================================================

install(DIRECTORY launch meshes urdf worlds DESTINATION share/${PROJECT_NAME}/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
