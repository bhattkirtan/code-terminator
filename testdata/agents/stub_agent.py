# Creates mock service files for backend APIs
def generate_stub_service(name):
    return f"export class {name}Service {{ getData() {{ return of([]); }} }}"
