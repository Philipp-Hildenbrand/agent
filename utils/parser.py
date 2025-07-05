# -- Parser Class --
class Parser:
    # Extract tool-calls
    def extract_tagged_sections(self, text: str) -> list[str] | str:
        extracted = []
        index = 0
        stack = []
        while index < len(text):
            start = text.find("<<<", index)
            end = text.find(">>>", index)
            if start == -1 and end == -1:
                break
            if end != -1 and (start == -1 or end < start):
                return "Error during parsing tool-format in your response"
            if start != -1:
                if stack:
                    return "Error during parsing tool-format in your response"
                stack.append(start)
                end = text.find(">>>", start)
                if end == -1:
                    return "Error during parsing tool-format in your response"
                content = text[start + 3:end]
                if "<<<" in content or ">>>" in content:
                    return "Error during parsing tool-format in your response"
                extracted.append(content)
                stack.pop()
                index = end + 3
            else:
                index += 1
        if stack:
            return "Error during parsing tool-format in your response"
        return extracted

    # Parse tool-call
    def parse_tool_call(self, block: str) -> list[str]:
        DELIMITER_STR = "<nex!-pr-amtre?gr+>"
        first_quote_index = block.find("'")
        if first_quote_index == -1:
            tool_name = block.strip()
            if tool_name.endswith(":"):
                tool_name = tool_name[:-1]
            return [tool_name]
        tool_name = block[:first_quote_index].strip()
        if tool_name.endswith(":"):
            tool_name = tool_name[:-1]
        params = [tool_name]
        params_string = block[first_quote_index:]
        parts_with_quotes = params_string.split(DELIMITER_STR)
        for part_with_quote in parts_with_quotes:
            if part_with_quote.startswith("'") and part_with_quote.endswith("'"):
                param_content = part_with_quote[1:-1]
                params.append(param_content)
            else:
                break
        return params