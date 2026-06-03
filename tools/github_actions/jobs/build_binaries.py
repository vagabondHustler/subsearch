from tools.github_actions.handlers import binaries


def main() -> None:
    binaries.write_to_hashes()
    binaries.prepare_build_artifacts()


if __name__ == "__main__":
    main()
