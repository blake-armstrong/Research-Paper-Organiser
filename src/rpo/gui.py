import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from .rpo import ResearchPaperOrganiser


class MainWindow(QMainWindow):
    def __init__(self, RPO: ResearchPaperOrganiser):
        super().__init__()
        self.setWindowTitle("Research Paper Organiser")
        self.setGeometry(100, 100, 800, 600)

        # config = get_config()
        # self.organiser = ResearchPaperOrganiser(config["db_path"], config["pdf_dir"])
        self.organiser = RPO

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Add Paper Tab
        add_tab = QWidget()
        add_layout = QVBoxLayout(add_tab)

        bibtex_label = QLabel("BibTeX:")
        self.bibtex_input = QTextEdit()
        add_layout.addWidget(bibtex_label)
        add_layout.addWidget(self.bibtex_input)

        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        file_button = QPushButton("Browse")
        file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(file_button)
        add_layout.addLayout(file_layout)

        keywords_layout = QHBoxLayout()
        self.keywords_input = QLineEdit()
        keywords_layout.addWidget(QLabel("Keywords:"))
        keywords_layout.addWidget(self.keywords_input)
        add_layout.addLayout(keywords_layout)

        add_button = QPushButton("Add Paper")
        add_button.clicked.connect(self.add_paper)
        add_layout.addWidget(add_button)

        tabs.addTab(add_tab, "Add Paper")

        # Search Tab
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)

        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_papers)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(search_button)
        search_layout.addLayout(search_input_layout)

        self.search_results = QTableWidget()
        self.search_results.setColumnCount(5)
        self.search_results.setHorizontalHeaderLabels(
            ["ID", "Authors", "Year", "Journal", "Title"]
        )
        self.search_results.cellDoubleClicked.connect(self.open_paper)
        search_layout.addWidget(self.search_results)

        tabs.addTab(search_tab, "Search Papers")

        # List All Papers Tab
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)

        list_button = QPushButton("List All Papers")
        list_button.clicked.connect(self.list_all_papers)
        list_layout.addWidget(list_button)

        self.papers_list = QTableWidget()
        self.papers_list.setColumnCount(5)
        self.papers_list.setHorizontalHeaderLabels(
            ["ID", "Authors", "Year", "Journal", "Title"]
        )
        self.papers_list.cellDoubleClicked.connect(self.open_paper)
        list_layout.addWidget(self.papers_list)

        tabs.addTab(list_tab, "List All Papers")

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_name:
            self.file_input.setText(file_name)

    def add_paper(self):
        bibtex = self.bibtex_input.toPlainText()
        file_path = self.file_input.text()
        keywords = [
            keyword.strip() for keyword in self.keywords_input.text().split(",")
        ]

        try:
            self.organiser.add_paper(bibtex, file_path, keywords)
            QMessageBox.information(self, "Success", "Paper added successfully.")
            self.bibtex_input.clear()
            self.file_input.clear()
            self.keywords_input.clear()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def search_papers(self):
        query = self.search_input.text()
        results = self.organiser.search_papers(query)
        self.populate_table(self.search_results, results)

    def list_all_papers(self):
        papers = self.organiser.list_all_papers()
        self.populate_table(self.papers_list, papers)

    def populate_table(self, table, papers):
        table.setRowCount(0)
        for row, paper in enumerate(papers):
            table.insertRow(row)
            for col, value in enumerate(paper[:5]):  # Exclude file_path
                item = QTableWidgetItem(str(value))
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )  # Make item read-only
                table.setItem(row, col, item)
        table.resizeColumnsToContents()

    def open_paper(self, row, column):
        paper_id = int(self.sender().item(row, 0).text())
        self.organiser.open_paper(paper_id)


def run_gui(RPO: ResearchPaperOrganiser):
    app = QApplication(sys.argv)
    window = MainWindow(RPO)
    window.show()
    sys.exit(app.exec())


# if __name__ == "__main__":
# main()
