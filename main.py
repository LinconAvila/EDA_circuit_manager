from hash import HashTable

class Cell:
    def __init__(self, id, width, height, x, row):
        self.id = id
        self.width = width
        self.height = height
        self.x = x
        self.row = row

class Circuit:
    def __init__(self, rows=145, row_width=2500, row_height=504):
        self.rows = [[] for _ in range(rows)]
        self.row_width = row_width
        self.row_height = row_height
        self.cells = HashTable(12028)
        self.loaded = False

    def insert_cell(self, id, width, height):
        for row_idx, row in enumerate(self.rows):
            current_x = 0
            for cell in row:
                if current_x + width <= cell.x:
                    new_cell = Cell(id, width, height, current_x, row_idx)
                    row.append(new_cell)
                    row.sort(key=lambda c: c.x)
                    self.cells.insert(id, new_cell)
                    return
                current_x = cell.x + cell.width
            
            if current_x + width <= self.row_width:
                new_cell = Cell(id, width, height, current_x, row_idx)
                row.append(new_cell)
                self.cells.insert(id, new_cell)
                return

    def search_cell(self, id):
        try:
            cell = self.cells.search(id)
            return (cell.row, cell.x)
        except KeyError:
            return None

    def remove_cell(self, id):
        try:
            cell = self.cells.search(id)
            self.rows[cell.row].remove(cell)
            self.cells.remove(id)
            return True
        except KeyError:
            return False

    def load_file(self, file):
        with open(file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3 and parts[0].startswith('a'):
                    id, width, height = parts
                    self.insert_cell(id, float(width), float(height))
        self.loaded = True