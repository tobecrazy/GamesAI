class Board {
    static WIDTH = 10;
    static HEIGHT = 20;
    static CELL_SIZE = 30; // Example size, can be adjusted in rendering

    constructor() {
        this.grid = this.createEmptyGrid();
    }

    createEmptyGrid() {
        return Array.from({ length: Board.HEIGHT }, () => Array(Board.WIDTH).fill(null));
    }

    isValidPosition(block) {
        for (let y = 0; y < block.shape.length; y++) {
            for (let x = 0; x < block.shape[y].length; x++) {
                if (block.shape[y][x]) { // If it's part of the block
                    const boardX = block.x + x;
                    const boardY = block.y + y;

                    // Check boundaries
                    if (boardX < 0 || boardX >= Board.WIDTH || boardY >= Board.HEIGHT || boardY < 0) {
                        return false;
                    }

                    // Check for collision with existing blocks on the board
                    if (this.grid[boardY] && this.grid[boardY][boardX]) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    placeBlock(block) {
        for (let y = 0; y < block.shape.length; y++) {
            for (let x = 0; x < block.shape[y].length; x++) {
                if (block.shape[y][x]) {
                    if (block.y + y < 0) {
                        // This situation (part of block is above the board)
                        // could indicate a game over condition if it's the initial placement.
                        // For now, we'll allow it, but game logic might handle it.
                        continue;
                    }
                    this.grid[block.y + y][block.x + x] = block.color;
                }
            }
        }
    }

    clearLines() {
        let linesCleared = 0;
        for (let y = Board.HEIGHT - 1; y >= 0; y--) {
            if (this.grid[y].every(cell => cell !== null)) {
                // Line is full
                linesCleared++;
                this.grid.splice(y, 1); // Remove the full line
                this.grid.unshift(Array(Board.WIDTH).fill(null)); // Add an empty line at the top
                y++; // Re-check the current line index as lines shifted
            }
        }
        return linesCleared;
    }

    // 'draw' and 'draw_ghost' will be handled by rendering logic.
    // 'get_ghost_position' can be added later if needed for game logic.
}
