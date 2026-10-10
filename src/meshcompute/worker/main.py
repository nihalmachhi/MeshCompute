"""Worker command-line entry point."""
import logging
from meshcompute.common.logging import configure_logging
from meshcompute.common.settings import get_settings
from meshcompute.worker.agent import run_worker

def main() -> None:
    """Configure worker logging and start the coordinator client loop."""
    settings=get_settings();configure_logging(settings.log_level)
    logging.getLogger(__name__).info("starting MeshCompute worker")
    run_worker()
if __name__=="__main__":main()
