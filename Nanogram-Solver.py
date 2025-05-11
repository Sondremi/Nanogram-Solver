def get_grid():
    """Get grid information from user with improved input methods"""
    print("\nNonogram Solver - Input Options:")
    print("1. Input in terminal")
    print("2. File input")
    
    while True:
        try:
            choice = input("\nChoose input method (1/2): ").strip()
            if choice == "1":
                return get_input()
            elif choice == "2":
                return get_file_input()
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

def get_input():
    """Get grid information from user in terminal"""
    while True:
        try:
            size = int(input("\nEnter the size of the grid (10, 15, or 20): "))
            if size not in [10, 15, 20]:
                print("Invalid size. Please choose 10, 15, or 20.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number (10, 15, or 20).")
    
    print(f"\nGrid size: {size}x{size}")

    def input_clues(direction):
        """Get clues for rows or columns"""
        print(f"\n--- {direction} Clues ---")
        print("Enter space-separated numbers for each column.")

        clue_list = []        
        for i in range(size):
            while True:
                try:
                    clue_input = input(f"{direction} {i + 1}: ").strip()
                    
                    if clue_input == "":
                        print("Please enter clues.")
                        continue
                    else:
                        clue_numbers = list(map(int, clue_input.split()))
                                    
                    min_length = sum(clue_numbers) + max(0, len(clue_numbers) - 1)
                    if min_length > size:
                        print(f"Size of clues exceeds grid size.")
                        continue
                    
                    clue_list.append(clue_numbers)
                    break
                except ValueError:
                    print("Please enter space-separated numbers.")
        return clue_list
    
    rows = input_clues("Row")
    cols = input_clues("Column")
    
    return size, rows, cols

def get_file_input():
    """Load grid information from a file"""
    filename = input("\nEnter filename: ").strip()
    filename += ".txt"
    try:
        with open(filename, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
            
            try:
                size = int(lines[0])
                if size not in [10, 15, 20]:
                    print(f"Invalid size: {size}. Please use 10, 15, or 20.")
                    return get_grid()
            except ValueError:
                print("First line must contain grid size (10, 15, or 20).")
                return get_grid()
            
            def file_clues(start_line):
                """Get clues for rows or columns"""
                clues_list = []
                for i in range(start_line, start_line + size):
                    if i >= len(lines):
                        print(f"File format error: missing lines")
                        return get_grid()
                    try:
                        clue_numbers = list(map(int, lines[i].split()))

                        min_length = sum(clue_numbers) + max(0, len(clue_numbers) - 1)
                        if min_length > size:
                            print(f"Size of clues for line {i+1} exceeds grid size.")
                            return get_grid()
                        
                        clues_list.append(clue_numbers)
                    except ValueError:
                        print(f"Invalid clues at line {i+1}. Must be space-separated numbers.")
                        return get_grid()
                return clues_list
            
            print("\n--- LOADED FROM FILE ---")
            print(f"Size: {size}x{size}\n")
            
            row_clues = file_clues(1)
            col_clues = file_clues(size+1)

            return size, row_clues, col_clues
            
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return get_grid()
    except Exception as e:
        print(f"Error reading file: {e}")
        print("File format should be:")
        print("Line 1: Grid size (10, 15, or 20)")
        print("Line 2 to size+1: Row clues")
        print("Line size+2 to 2*size+1: Column clues")
        return get_grid()

def is_valid_line(line, clues):
    """Check if a line matches the clues"""
    blocks = []
    count = 0
    
    for cell in line:
        if cell == '■':
            count += 1
        elif count > 0:
            blocks.append(count)
            count = 0
    
    if count > 0:
        blocks.append(count)
    
    return blocks == clues

def get_possible_lines(length, clues):
    """Generate all possible valid line configurations for given clues"""
    possible_lines = []
    
    def backtrack(line, idx, block_idx, current_block_size):
        # Base case: reached the end of the line
        if idx == length:
            # If we've placed all blocks correctly
            if block_idx == len(clues) and current_block_size == 0:
                possible_lines.append(line.copy())
            # Or if we're on the last block and it's the right size
            elif block_idx == len(clues) - 1 and current_block_size == clues[block_idx]:
                possible_lines.append(line.copy())
            return
        
        line[idx] = '■'
        if current_block_size + 1 <= (clues[block_idx] if block_idx < len(clues) else 0):
            backtrack(line, idx + 1, block_idx, current_block_size + 1)
            
        line[idx] = 'x'
        if current_block_size == 0:
            # No block in progress, just continue
            backtrack(line, idx + 1, block_idx, 0)
        elif current_block_size == clues[block_idx]:
            # We've just completed a block, move to the next one
            backtrack(line, idx + 1, block_idx + 1, 0)
    
    line = ['x'] * length
    backtrack(line, 0, 0, 0)
    return possible_lines

def solve(size, rows, cols):
    """Solve the nonogram puzzle"""
    grid = [[None for _ in range(size)] for _ in range(size)]
    
    row_possibilities = []
    col_possibilities = []
        
    for _, row_clues in enumerate(rows):
        row_possibilities.append(get_possible_lines(size, row_clues))
    
    for _, col_clues in enumerate(cols):
        col_possibilities.append(get_possible_lines(size, col_clues))
    
    def update_grid():
        """Update grid based on current possibilities"""
        changes = False
        
        for i in range(size):
            for j in range(size):
                cell_values = set(line[j] for line in row_possibilities[i])
                if len(cell_values) == 1 and grid[i][j] != list(cell_values)[0]:
                    grid[i][j] = list(cell_values)[0]
                    changes = True
        
        for j in range(size):
            for i in range(size):
                cell_values = set(line[i] for line in col_possibilities[j])
                if len(cell_values) == 1 and grid[i][j] != list(cell_values)[0]:
                    grid[i][j] = list(cell_values)[0]
                    changes = True
        
        return changes
    
    def filter_possibilities():
        """Filter possibilities based on current grid state"""
        changes = False
        
        for row in range(size):
            new_possibilities = []
            for line in row_possibilities[row]:
                valid = True
                for i in range(size):
                    if grid[row][i] is not None and line[i] != grid[row][i]:
                        valid = False
                        break
                if valid:
                    new_possibilities.append(line)
            
            if len(new_possibilities) < len(row_possibilities[row]):
                row_possibilities[row] = new_possibilities
                changes = True
        
        for col in range(size):
            new_possibilities = []
            for line in col_possibilities[col]:
                valid = True
                for i in range(size):
                    if grid[i][col] is not None and line[i] != grid[i][col]:
                        valid = False
                        break
                if valid:
                    new_possibilities.append(line)
            
            if len(new_possibilities) < len(col_possibilities[col]):
                col_possibilities[col] = new_possibilities
                changes = True
        
        return changes
    
    changes = True
    while changes:
        changes = update_grid() or filter_possibilities()
    
    # Return solution if grid is complete
    if not any(None in row for row in grid):
        return grid
    
    # Solve with backtracking    
    # Create a copy of the partially solved grid
    partial_grid = [row[:] for row in grid]
    
    def backtrack_solve(grid, row, col):
        """Use backtracking and try to guess block placements"""
        if row >= size:
            for i in range(size):
                if not is_valid_line(grid[i], rows[i]):
                    return None
            
            for j in range(size):
                col_line = [grid[i][j] for i in range(size)]
                if not is_valid_line(col_line, cols[j]):
                    return None
                    
            return grid
        
        next_row = row
        next_col = col + 1
        if next_col >= size:
            next_row += 1
            next_col = 0
        
        if grid[row][col] is not None:
            return backtrack_solve(grid, next_row, next_col)
        
        grid[row][col] = '■'
        result = backtrack_solve(grid, next_row, next_col)
        if result:
            return result
        
        grid[row][col] = 'x'
        result = backtrack_solve(grid, next_row, next_col)
        if result:
            return result
        
        grid[row][col] = None
        return None
    
    return backtrack_solve(partial_grid, 0, 0)

def print_grid(grid, rows, cols):
    size = len(grid)
    
    max_row_clues = max(len(row) for row in rows)
    max_col_clues = max(len(col) for col in cols)
    
    cell_width = 3
    
    # Column clues
    for i in range(max_col_clues):
        print(' ' * (max_row_clues * cell_width + 1), end='')
        
        for j in range(size):
            if i >= max_col_clues - len(cols[j]):
                clue_index = i - (max_col_clues - len(cols[j]))
                print(f"{cols[j][clue_index]:^{cell_width}}", end='')
            else:
                print(' ' * cell_width, end='')
                
            # Vertical divider after every 5th column
            if (j + 1) % 5 == 0 and j < size - 1:
                print(' ', end='')
        print()
    
    # Horizontal divider every 5th column
    separator_line = '─' * cell_width
    top_line = ' ' * (max_row_clues * cell_width) + '┌'
    for j in range(size):
        top_line += separator_line
        if (j + 1) % 5 == 0 and j < size - 1:
            top_line += '┬'
        elif j == size - 1:
            top_line += '┐'
    print(top_line)
    
    # Row clues
    for i, row in enumerate(grid):
        for j in range(max_row_clues):
            if j >= max_row_clues - len(rows[i]):
                clue_index = j - (max_row_clues - len(rows[i]))
                print(f"{rows[i][clue_index]:>{cell_width}}", end='')
            else:
                print(' ' * cell_width, end='')
        
        print('│', end='')
        
        for j, cell in enumerate(row):
            print(f"{cell:^{cell_width}}", end='')
            # Vertical divider every 5th column
            if (j + 1) % 5 == 0 and j < size - 1:
                print('│', end='')
            elif j == size - 1:
                print('│', end='')
        print()
        
        # Horizontal divider every 5th row
        if (i + 1) % 5 == 0 and i < size - 1:
            divider_line = ' ' * (max_row_clues * cell_width) + '├'
            for j in range(size):
                divider_line += '─' * cell_width
                if (j + 1) % 5 == 0 and j < size - 1:
                    divider_line += '┼'
                elif j == size - 1:
                    divider_line += '┤'
            print(divider_line)
    
    # Bottom horizontal line
    bottom_line = ' ' * (max_row_clues * cell_width) + '└'
    for j in range(size):
        bottom_line += '─' * cell_width
        if (j + 1) % 5 == 0 and j < size - 1:
            bottom_line += '┴'
        elif j == size - 1:
            bottom_line += '┘'
    print(bottom_line)

def save_grid(grid, rows, cols, size):
    """Save solution to file"""
    filename = input("\nEnter filename to save (or press Enter to skip): ").strip()
    if filename:
        filename += ".txt"
    else:
        return
    
    try:
        with open(filename, 'w') as file:
            def file_print(*args, end='\n', sep=' '):
                file.write(sep.join(map(str, args)) + end)
            
            file_print("--- INPUT ---")
            file_print(f"{size}")
            
            for row in rows:
                file_print(' '.join(map(str, row)))
            
            for col in cols:
                file_print(' '.join(map(str, col)))
            
            if grid:
                file_print("\n--- SOLUTION ---")

                max_row_clues = max(len(row) for row in rows)
                max_col_clues = max(len(col) for col in cols)
                cell_width = 3
                
                # Column clues
                for i in range(max_col_clues):
                    file_print(' ' * (max_row_clues * cell_width + 1), end='')
                    
                    for j in range(size):
                        if i >= max_col_clues - len(cols[j]):
                            clue_index = i - (max_col_clues - len(cols[j]))
                            file_print(f"{cols[j][clue_index]:^{cell_width}}", end='')
                        else:
                            file_print(' ' * cell_width, end='')
                            
                        # Vertical divider after every 5th column
                        if (j + 1) % 5 == 0 and j < size - 1:
                            file_print(' ', end='')
                    file_print()
                
                # Horizontal divider
                separator_line = '─' * cell_width
                top_line = ' ' * (max_row_clues * cell_width) + '┌'
                for j in range(size):
                    top_line += separator_line
                    if (j + 1) % 5 == 0 and j < size - 1:
                        top_line += '┬'
                    elif j == size - 1:
                        top_line += '┐'
                file_print(top_line)
                
                # Row clues and grid
                for i, row in enumerate(grid):
                    for j in range(max_row_clues):
                        if j >= max_row_clues - len(rows[i]):
                            clue_index = j - (max_row_clues - len(rows[i]))
                            file_print(f"{rows[i][clue_index]:>{cell_width}}", end='')
                        else:
                            file_print(' ' * cell_width, end='')
                    
                    file_print('│', end='')
                    
                    for j, cell in enumerate(row):
                        file_print(f"{cell:^{cell_width}}", end='')
                        # Vertical divider every 5th column
                        if (j + 1) % 5 == 0 and j < size - 1:
                            file_print('│', end='')
                        elif j == size - 1:
                            file_print('│', end='')
                    file_print()
                    
                    # Horizontal divider every 5th row
                    if (i + 1) % 5 == 0 and i < size - 1:
                        divider_line = ' ' * (max_row_clues * cell_width) + '├'
                        for j in range(size):
                            divider_line += '─' * cell_width
                            if (j + 1) % 5 == 0 and j < size - 1:
                                divider_line += '┼'
                            elif j == size - 1:
                                divider_line += '┤'
                        file_print(divider_line)
                
                # Bottom horizontal line
                bottom_line = ' ' * (max_row_clues * cell_width) + '└'
                for j in range(size):
                    bottom_line += '─' * cell_width
                    if (j + 1) % 5 == 0 and j < size - 1:
                        bottom_line += '┴'
                    elif j == size - 1:
                        bottom_line += '┘'
                file_print(bottom_line)
                
                file_print("\n--- BINARY REPRESENTATION ---")
                for row in grid:
                    file_print(''.join('1' if cell == '■' else '0' for cell in row))
        
        print(f"Grid saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def main():
    print("\n=== NONOGRAM SOLVER ===")
    print("This program helps solve nonogram puzzles.")
    
    size, rows, cols = get_grid()

    solved_grid = solve(size, rows, cols)
    
    if solved_grid:
        print("\nSolution found!\n")
        print_grid(solved_grid, rows, cols)
        save_grid(solved_grid, rows, cols, size)
    else:
        print("\nNo solution found. The puzzle might be invalid or too complex.")
        print("Please check the clues and try again.")
        
        print("\nTry again? (y/n): ", end='')
        if input().strip().lower() == 'y':
            main()

if __name__ == "__main__":
    main()
