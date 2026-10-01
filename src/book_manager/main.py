from book_manager.preload_data.preload_data import generar_csvs
from book_manager.ui.console import ConsoleUI, Servicios


def main(import_default_data: bool = False) -> None:
    if import_default_data:
        generar_csvs(sobrescribir=True)
    ConsoleUI(Servicios()).run()


if __name__ == "__main__":
    main()
