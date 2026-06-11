import time
from stage_controller import StageController

# Velocity in mm/s 
VELOCITY_MM_S = 0.0006
VELOCITY_MM_S_STEPPED = 1.00

# Mode: 'continuous' or 'stepped'
MODE = "continuous"

# For continuous mode: total distance to move in mm
TOTAL_DISTANCE_MM = 0.01

# For stepped mode: step size and number of steps
STEP_SIZE_MM = 0.00001
STEPS = 100
# --------------------------------------------------


def main():
    stage = StageController()

    if not stage.connect():
        print("Stage connection failed")
        return

    current_position = stage.get_position()

    # Apply velocity to controller (no acceleration used)
    

    if MODE.lower().startswith("c"):
        stage.set_velocity(VELOCITY_MM_S)
        final_target = stage.clamp_position(current_position + TOTAL_DISTANCE_MM)

        print(f"Continuous move to {final_target:.6f} mm at {VELOCITY_MM_S} mm/s")

        if not stage.move_absolute(final_target):
            print("Move command failed")
        else:
            while stage.is_moving:
                time.sleep(0.02)

            current_position = stage.get_position()

    else:
        stage.set_velocity(VELOCITY_MM_S_STEPPED)
        print(f"Stepped mode: {STEPS} steps of {STEP_SIZE_MM} mm at {VELOCITY_MM_S_STEPPED} mm/s")

        for step in range(STEPS):
            next_position = stage.clamp_position(current_position + STEP_SIZE_MM)

            print(f"Step {step + 1}/{STEPS}: move to {next_position:.7f} mm")

            if not stage.move_absolute(next_position):
                print("Move command failed")
                break

            while stage.is_moving:
                time.sleep(0.02)

            current_position = stage.get_position()

    stage.close()
    print("Done. Stage connection closed.")


if __name__ == "__main__":
    main()
