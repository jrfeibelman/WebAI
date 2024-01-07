
from logging import DEBUG, INFO
from argparse import ArgumentParser
from os import path, makedirs, getcwd
from dotenv import load_dotenv
from sys import exit, stdout

from rtai.story.engine import StoryEngine
from rtai.utils.config import YamlLoader
from rtai.utils.logging import setup_logging, info

LOGGER_CONFIG = "Logger"

def parse_args() -> dict:
    ap = ArgumentParser()
    ap.add_argument("-c", "--config_file", help="set config file", type=str, default="configs/rtai.yaml")
    ap.add_argument("-t", "--test_mode", help="set test mode", action='store_true')

    args = vars(ap.parse_args())
    return args

if __name__ == "__main__":
    # Environment setup
    load_dotenv()

    # Parse Args
    args = parse_args()
    config_file = args['config_file']
    test_mode = args['test_mode']

    if not path.exists(config_file):
        print("Error: config file %s does not exist" % config_file)
        exit(1)

    log_level = DEBUG
    cfg = YamlLoader.load(config_file)

    if cfg.contains(LOGGER_CONFIG):
        log_cfg = cfg.expand(LOGGER_CONFIG)
        
        # Setup Logging
        log_dir: str = log_cfg.get_value('LogDirectory', '%s/logs/' % getcwd())
        log_name: str = log_cfg.get_value('LogName', 'rtai')
        log_level: int = INFO if log_cfg.get_value('Level', 'INFO') == 'INFO' else DEBUG
        log_stdout_pipe: bool = log_cfg.get_value('PipeToStdout', 'False') == 'True'
        use_callee_stack: bool = log_cfg.get_value('UseCalleeStack', 'False') == 'True'
        transcript_log_name: str = log_cfg.get_value('TranscriptLogName', '')

        setup_logging(log_dir, log_name, log_level, transcript_log_name, use_callee_stack, log_stdout_pipe)

    # Create Engine
    engine = StoryEngine(cfg, debug_mode=log_level == DEBUG, test_mode=test_mode)
    engine.start()