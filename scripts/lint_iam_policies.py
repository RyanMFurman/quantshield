from __future__ import annotations

import re
import sys
from pathlib import Path


READ_ONLY_PREFIXES = ("describe", "get", "list")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("terraform")
    findings = lint_terraform_iam_policies(root)
    if findings:
        print("IAM policy lint failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("IAM policy lint passed: no wildcard actions, AdministratorAccess, or mutating Resource '*' statements found.")
    return 0


def lint_terraform_iam_policies(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*.tf"):
        content = path.read_text(encoding="utf-8")
        for block_name, block in _policy_document_blocks(content):
            for statement_index, statement in enumerate(_statement_blocks(block), start=1):
                actions = _extract_list_values(statement, "actions")
                resources = _extract_list_values(statement, "resources")
                statement_name = f"{block_name}.statement[{statement_index}]"

                if any(action == "*" or action.endswith(":*") for action in actions):
                    findings.append(f"{path}:{statement_name} contains wildcard action")

                if any(value == "AdministratorAccess" for value in _all_quoted_values(statement)):
                    findings.append(f"{path}:{statement_name} references AdministratorAccess")

                if "*" in resources:
                    mutating = [action for action in actions if not _is_read_only_action(action)]
                    if mutating:
                        findings.append(f"{path}:{statement_name} uses Resource '*' with mutating actions: {', '.join(mutating)}")

    return findings


def _policy_document_blocks(content: str) -> list[tuple[str, str]]:
    starts = list(re.finditer(r'data\s+"aws_iam_policy_document"\s+"([^"]+)"\s+\{', content))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(starts):
        start = match.end()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(content)
        blocks.append((match.group(1), content[start:end]))
    return blocks


def _statement_blocks(block: str) -> list[str]:
    starts = list(re.finditer(r"statement\s+\{", block))
    statements: list[str] = []
    for index, match in enumerate(starts):
        start = match.end()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(block)
        statements.append(block[start:end])
    return statements


def _extract_list_values(block: str, attr: str) -> list[str]:
    values: list[str] = []
    for list_match in re.finditer(rf"{attr}\s*=\s*\[(.*?)\]", block, re.DOTALL):
        values.extend(re.findall(r'"([^"]+)"', list_match.group(1)))
    for scalar_match in re.finditer(rf'{attr}\s*=\s*"([^"]+)"', block):
        values.append(scalar_match.group(1))
    return values


def _all_quoted_values(block: str) -> list[str]:
    return re.findall(r'"([^"]+)"', block)


def _is_read_only_action(action: str) -> bool:
    if ":" not in action:
        return False
    verb = action.split(":", 1)[1].lower()
    return verb.startswith(READ_ONLY_PREFIXES)


if __name__ == "__main__":
    raise SystemExit(main())
