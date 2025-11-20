from pathlib import Path

def parse_structure(file_path, output_dir='.'):
    output_base = Path(output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'r') as file:
        lines = file.readlines()

    parsed_lines = []
    for line in lines:
        stripped = line.rstrip('\n')
        name = stripped.strip()
        if not name:
            continue  # Skip empty lines

        indent = len(stripped) - len(stripped.lstrip(' \t'))

        parsed_lines.append({
            'name': name,
            'indent': indent,
            'is_dir': name.endswith('/')
        })

    for i, item in enumerate(parsed_lines):
        if i  < len(parsed_lines) - 1:
            next_indent = parsed_lines[i + 1]['indent']
            if next_indent > item['indent']:
                item['is_dir'] = True

    path_stack = []

    for item in parsed_lines:
        indent = item['indent']
        name = item['name'].rstrip('/')

        while path_stack and path_stack[-1]['indent'] >= indent:
            path_stack.pop()

        if path_stack:
            full_path = output_base / path_stack[-1]['path'] / name
        else:
            full_path = output_base / name

        if item['is_dir']:
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()

        if item['is_dir']:
            path_stack.append({'path': name if not path_stack else f"{path_stack[-1]['path']}/{name}", 'indent': indent})

def main():
    file_path = 'example.txt'
    output_dir = 'output'
    parse_structure(file_path, output_dir)

if __name__ == "__main__":
    main()
