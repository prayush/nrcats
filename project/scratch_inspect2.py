import sxs


def main():
    sim_name = "SXS:BBH:0058"
    try:
        sim = sxs.load(sim_name, auto_supersede=True)
        h = sim.horizons

        t0 = h.A.time[0]
        print(f"t0: {t0}")
        if hasattr(h, "nhat"):
            print("nhat at t0:", h.nhat[0])
            print("ellhat at t0:", h.ellhat[0])
        else:
            print("No nhat in Horizons!")

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
