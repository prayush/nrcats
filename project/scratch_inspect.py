import sxs


def main():
    sim_name = "SXS:BBH:0058"
    try:
        horizons = sxs.load(f"{sim_name}/Horizons.h5")
        print("Horizons loaded successfully.")
        print(dir(horizons))
        print("A keys:", list(horizons.A.keys()) if hasattr(horizons, "A") else "No A")
        print(
            "chiInertial for A:",
            horizons.A.chiInertial
            if hasattr(horizons.A, "chiInertial")
            else "No chiInertial",
        )
        print(
            "time for A:", horizons.A.time if hasattr(horizons.A, "time") else "No time"
        )
    except Exception as e:
        print(f"Failed to load: {e}")


if __name__ == "__main__":
    main()
