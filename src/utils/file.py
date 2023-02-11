import json
import re
from asyncio.log import logger

import jsonschema
from jsonschema import Draft202012Validator, validate
from rich.console import Console
from rich.table import Table

from OMRChecker.src.constants import SCHEMA_DEFAULTS_PATH


def load_json(path, **rest):
    with open(path, "r") as f:
        loaded = json.load(f, **rest)
    return loaded


execute_api_schema = load_json(SCHEMA_DEFAULTS_PATH)
VALIDATOR = Draft202012Validator(execute_api_schema)


def validate_json(json_data, template_path):

    logger.info("Validating template.json ...")
    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:

        table = Table(show_lines=True)
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Error", style="magenta")

        errors = sorted(VALIDATOR.iter_errors(json_data), key=lambda e: e.path)
        for error in errors:
            key, validator, msg = error.path[0], error.validator, error.message

            # Print preProcessor name in case of options error
            if key == "preProcessors":
                preProcessorName = json_data["preProcessors"][error.path[1]]["name"]
                preProcessorKey = error.path[2]
                table.add_row(f"{key}.{preProcessorName}.{preProcessorKey}", msg)
            elif validator == "required":
                table.add_row(
                    re.findall(r"'(.*?)'", msg)[0],
                    msg
                    + ". Make sure the spelling of the key is correct and it is in camelCase",
                )
            else:
                table.add_row(key, msg)
        console = Console()
        console.print(table)
        err = f"Provided Template JSON is Invalid: {template_path}"
        return False, err

    message = "Template JSON validated successfully..."
    return True, message
