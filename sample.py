from visualization.view import view

for file in ["2022-08-11", "2022-08-12"]:
    view(f"{file}.rview", f"{file}.html", False)