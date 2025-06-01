class Block {
    constructor(shape, color, x = 0, y = 0) {
        this.shape = shape;
        this.color = color;
        this.x = x; // Represents the column index of the block's top-left corner
        this.y = y; // Represents the row index of the block's top-left corner
    }

    static SHAPES = [
        // I
        [[1, 1, 1, 1]],
        // J
        [[1, 0, 0],
         [1, 1, 1]],
        // L
        [[0, 0, 1],
         [1, 1, 1]],
        // O
        [[1, 1],
         [1, 1]],
        // S
        [[0, 1, 1],
         [1, 1, 0]],
        // T
        [[0, 1, 0],
         [1, 1, 1]],
        // Z
        [[1, 1, 0],
         [0, 1, 1]]
    ];

    static COLORS = [
        'cyan',    // I
        'blue',    // J
        'orange',  // L
        'yellow',  // O
        'green',   // S
        'purple',  // T
        'red'      // Z
    ];

    static random() {
        const shapeIndex = Math.floor(Math.random() * Block.SHAPES.length);
        const shape = Block.SHAPES[shapeIndex];
        const color = Block.COLORS[shapeIndex];
        // For simplicity, let's assume initial x is roughly centered.
        // This might need adjustment based on board width and block shape.
        let x = Math.floor((10 - shape[0].length) / 2); // Assuming board width 10 for now
        return new Block(shape, color, x, 0);
    }

    rotate() {
        const newShape = [];
        const rows = this.shape.length;
        const cols = this.shape[0].length;

        for (let j = 0; j < cols; j++) {
            newShape[j] = [];
            for (let i = rows - 1; i >= 0; i--) {
                newShape[j].push(this.shape[i][j]);
            }
        }
        this.shape = newShape;
    }

    move(dx, dy) {
        this.x += dx;
        this.y += dy;
    }

    toDict() {
        return {
            shape: this.shape,
            color: this.color,
            x: this.x,
            y: this.y
        };
    }

    static fromDict(data) {
        const block = new Block(data.shape, data.color, data.x, data.y);
        return block;
    }

    // The 'draw' method will be handled by the rendering logic on the Canvas.
}
