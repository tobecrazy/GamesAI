class Game {
    constructor(canvas, scoreDisplay, levelDisplay, linesDisplay, nextBlockCanvas) {
        this.canvas = canvas;
        this.scoreDisplay = scoreDisplay;
        this.levelDisplay = levelDisplay;
        this.linesDisplay = linesDisplay;
        this.nextBlockCanvas = nextBlockCanvas;

        this.ctx = this.canvas.getContext('2d');
        this.nextBlockCtx = this.nextBlockCanvas.getContext('2d');

        this.sound = new Sound(); // Instantiate Sound
        this.sound.initBackgroundMusic('assets/background.mp3');
        this.sound.loadSound('clear', 'assets/clear.mp3');
        this.sound.loadSound('drop', 'assets/drop.mp3');
        this.sound.loadSound('gameover', 'assets/gameover.mp3');
        this.sound.loadSound('rotate', 'assets/rotate.mp3');
        // Add a flag to ensure user interaction has occurred before playing sounds automatically
        this.userInteracted = false;

        this.board = new Board();
        this.currentBlock = null;
        this.nextBlock = null;

        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;

        this.gameOver = false;
        this.paused = false;

        this.fallSpeed = 1000; // milliseconds
        this.lastFallTime = 0;

        // Adjust canvas dimensions based on board and cell size
        this.canvas.width = Board.WIDTH * Board.CELL_SIZE;
        this.canvas.height = Board.HEIGHT * Board.CELL_SIZE;

        // Adjust next block canvas (e.g., 4x4 cells)
        this.nextBlockCanvas.width = 4 * Board.CELL_SIZE;
        this.nextBlockCanvas.height = 4 * Board.CELL_SIZE;

        this.lineClearPoints = [0, 100, 300, 500, 800]; // Points for 0, 1, 2, 3, 4 lines
        this.HIGH_SCORES_KEY = 'tetrisHighScores';
        this.SAVED_GAME_KEY = 'tetrisSavedGame'; // localStorage key for saved game
    }

    // --- Save/Load Game State Methods ---
    saveGameState() {
        if (this.gameOver || !this.currentBlock) {
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = this.gameOver ? "Game Over. Cannot save." : "Cannot save an empty game.";
                setTimeout(() => { if(this.gameMessagesElement.textContent === (this.gameOver ? "Game Over. Cannot save." : "Cannot save an empty game.")) this.gameMessagesElement.textContent = "";}, 2000);
            }
            console.warn("Attempted to save game when game is over or currentBlock is null.");
            return;
        }

        const gameState = {
            boardGrid: this.board.grid,
            currentBlock: this.currentBlock ? this.currentBlock.toDict() : null,
            nextBlock: this.nextBlock ? this.nextBlock.toDict() : null,
            score: this.score,
            level: this.level,
            linesCleared: this.linesCleared,
            fallSpeed: this.fallSpeed,
            // lastFallTime is tricky. Saving absolute performance.now() value isn't ideal across sessions.
            // For simplicity, we'll reset it on load, or save a relative time if needed (more complex).
            // For now, not saving lastFallTime directly, will reset on load.
        };

        try {
            localStorage.setItem(this.SAVED_GAME_KEY, JSON.stringify(gameState));
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = "Game Saved!";
                setTimeout(() => { if(this.gameMessagesElement.textContent === "Game Saved!") this.gameMessagesElement.textContent = ""; }, 1500);
            }
            console.log("Game state saved.");
        } catch (error) {
            console.error("Error saving game state:", error);
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = "Error saving game.";
                 setTimeout(() => { if(this.gameMessagesElement.textContent === "Error saving game.") this.gameMessagesElement.textContent = ""; }, 1500);
            }
        }
    }

    loadGameState() {
        try {
            const savedStateJSON = localStorage.getItem(this.SAVED_GAME_KEY);
            if (!savedStateJSON) {
                if (this.gameMessagesElement) {
                    this.gameMessagesElement.textContent = "No saved game found.";
                    setTimeout(() => { if(this.gameMessagesElement.textContent === "No saved game found.") this.gameMessagesElement.textContent = ""; }, 1500);
                }
                console.log("No saved game found.");
                return false;
            }

            const loadedState = JSON.parse(savedStateJSON);

            this.board.grid = loadedState.boardGrid;
            this.currentBlock = loadedState.currentBlock ? Block.fromDict(loadedState.currentBlock) : null;
            this.nextBlock = loadedState.nextBlock ? Block.fromDict(loadedState.nextBlock) : null;
            this.score = loadedState.score;
            this.level = loadedState.level;
            this.linesCleared = loadedState.linesCleared;
            this.fallSpeed = loadedState.fallSpeed;

            this.lastFallTime = performance.now(); // Reset to current time to prevent immediate drop

            this.gameOver = false; // Loaded game is not game over
            this.paused = false;   // Unpause on load

            this.updateDisplays();
            if (this.gameMessagesElement) this.gameMessagesElement.textContent = "Game Loaded!";
            setTimeout(() => { if(this.gameMessagesElement && this.gameMessagesElement.textContent === "Game Loaded!") this.gameMessagesElement.textContent = ""; }, 1500);

            this.sound.stopBackgroundMusic(); // Stop current music if any
            this.sound.startBackgroundMusic(); // Start music for loaded game

            this.draw(); // Redraw the game with loaded state
            this.gameLoop(); // Ensure game loop continues/restarts

            console.log("Game state loaded.");
            return true;

        } catch (error) {
            console.error("Error loading game state:", error);
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = "Error loading saved game.";
                 setTimeout(() => { if(this.gameMessagesElement.textContent === "Error loading saved game.") this.gameMessagesElement.textContent = ""; }, 1500);
            }
            return false;
        }
    }
    // --- End Save/Load Game State Methods ---


    // --- High Score Methods ---
    getHighScores() {
        try {
            const scoresJSON = localStorage.getItem(this.HIGH_SCORES_KEY);
            return scoresJSON ? JSON.parse(scoresJSON) : [];
        } catch (error) {
            console.error("Error retrieving high scores from localStorage:", error);
            return [];
        }
    }

    saveHighScore(playerName, score) {
        if (!playerName) return; // Don't save if no name is provided
        try {
            const scores = this.getHighScores();
            const newScore = { name: playerName, score: score, date: new Date().toISOString() };
            scores.push(newScore);
            scores.sort((a, b) => b.score - a.score); // Sort descending
            const topScores = scores.slice(0, 10); // Keep only top 10
            localStorage.setItem(this.HIGH_SCORES_KEY, JSON.stringify(topScores));
        } catch (error) {
            console.error("Error saving high score to localStorage:", error);
        }
    }

    displayHighScores() {
        if (!this.gameMessagesElement) return;

        const highScores = this.getHighScores();
        let message = "<strong>High Scores:</strong><br>";
        if (highScores.length === 0) {
            message += "No high scores yet!<br>";
        } else {
            message += "<ol style='padding-left: 20px; text-align: left;'>"; // Basic styling for list
            highScores.forEach((score, index) => {
                message += `<li>${score.name}: ${score.score}</li>`;
            });
            message += "</ol>";
        }
        message += "<br>Press R to Restart.";
        this.gameMessagesElement.innerHTML = message; // Use innerHTML for <br> and list
    }

    // --- End High Score Methods ---


    init() {
        this.board = new Board(); // Re-initialize board
        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;
        this.gameOver = false;
        this.paused = false;
        this.fallSpeed = 1000;
        this.lastFallTime = performance.now(); // Reset fall time

        if (this.gameMessagesElement) { // Clear any previous messages
            this.gameMessagesElement.textContent = "";
        }

        this.currentBlock = null; // Explicitly nullify before generating new ones
        this.nextBlock = null;
        this.generateNewBlock(); // Generates current and next
        this.generateNewBlock(); // Sets current to former next, and generates a new next

        this.updateDisplays();
    }

    generateNewBlock() {
        // if (this.gameOver) return; // Game over is checked after attempting to place a new block

        this.currentBlock = this.nextBlock;
        this.nextBlock = Block.random();

        if (this.currentBlock === null) { // First block of the game (or after restart)
            this.currentBlock = Block.random();
        }

        // Set initial position for the current block
        this.currentBlock.x = Math.floor(Board.WIDTH / 2) - Math.floor(this.currentBlock.shape[0].length / 2);
        this.currentBlock.y = 0; // Start at the top

        if (!this.board.isValidPosition(this.currentBlock)) {
            this.gameOver = true;
            this.sound.stopBackgroundMusic();
            this.sound.playSound('gameover');
        }
        this.drawNextBlock(); // Update next block display
    }

    gameLoop(currentTime = 0) {
        if (this.gameOver) {
            // Game over logic handled in placeBlock or generateNewBlock where it's detected
            // Display logic for high scores will be triggered there too.
            this.draw(); // Draw the final state once
            return;
        }

        if (this.paused) {
            // Message is set in togglePause()
            // Keep drawing to show the paused screen, but no game logic updates
            this.draw();
            requestAnimationFrame(this.gameLoop.bind(this));
            return;
        }

        // Clear any non-persistent messages if game is running
        if (this.gameMessagesElement && (this.gameMessagesElement.textContent === "Paused." || this.gameMessagesElement.textContent.startsWith("Game Over!"))) {
             // Only clear if it's a pause or game over message, other messages might be important
        } else if (this.gameMessagesElement) {
            this.gameMessagesElement.textContent = "";
        }


        if (currentTime - this.lastFallTime > this.fallSpeed) {
            if (!this.tryMoveBlock(0, 1)) { // Attempt to move down
                // Block has landed or collision occurred
                this.placeBlock();
            }
            this.lastFallTime = currentTime;
        }

        this.draw(); // Draw the game state
        requestAnimationFrame(this.gameLoop.bind(this));
    }

    placeBlock() {
        if (!this.currentBlock) return;

        this.board.placeBlock(this.currentBlock);
        const cleared = this.board.clearLines();

        if (cleared > 0) {
            this.updateScore(cleared);
            this.linesCleared += cleared;
            this.updateLevel();
            this.updateFallSpeed();
            this.updateDisplays();
            this.sound.playSound('clear');
        }
        this.generateNewBlock();

        if (this.gameOver) {
            // This is where game over is definitively known after an attempted block placement
            if (this.score > 0) {
                // Check if current score is a high score before prompting
                const highScores = this.getHighScores();
                const lowestHighScore = highScores.length < 10 ? 0 : highScores[highScores.length -1].score;
                if (this.score > lowestHighScore || highScores.length < 10) {
                    const playerName = prompt(`Game Over! Your score: ${this.score}. Enter your name:`, 'Player');
                    if (playerName) { // If player provides a name (doesn't hit cancel or leave empty)
                        this.saveHighScore(playerName, this.score);
                    }
                } else {
                     if(this.gameMessagesElement) this.gameMessagesElement.textContent = `Game Over! Final Score: ${this.score}. Press R to Restart.`;
                }
            } else {
                 if(this.gameMessagesElement) this.gameMessagesElement.textContent = `Game Over! Final Score: ${this.score}. Press R to Restart.`;
            }
            this.displayHighScores(); // Always display high scores at game over
            // The gameLoop will return on the next frame because this.gameOver is true.
        }
    }

    tryMoveBlock(dx, dy) {
        if (!this.currentBlock || this.gameOver || this.paused) return true; // true = successful (no action taken or allowed)

        this.currentBlock.move(dx, dy);
        if (!this.board.isValidPosition(this.currentBlock)) {
            this.currentBlock.move(-dx, -dy); // Move back
            return false; // Move was invalid
        }
        return true; // Move was valid
    }

    moveBlock(dx) { // Simplified for horizontal movement, vertical is handled by game loop or drop
        this.tryMoveBlock(dx, 0);
    }

    rotateBlock() {
        if (!this.currentBlock || this.gameOver || this.paused) return;

        this.currentBlock.rotate();
        if (!this.board.isValidPosition(this.currentBlock)) {
            // If rotation is invalid, try to "wall kick" (simple version)
            // Try moving one unit left
            this.currentBlock.move(-1,0);
            if (!this.board.isValidPosition(this.currentBlock)) {
                this.currentBlock.move(1,0); // Move back
                 // Try moving one unit right
                this.currentBlock.move(1,0);
                if (!this.board.isValidPosition(this.currentBlock)) {
                    this.currentBlock.move(-1,0); // Move back
                    this.currentBlock.rotate(); // Rotate back (3 times for one counter-rotation)
                    this.currentBlock.rotate();
                    this.currentBlock.rotate();
                }
            }
        }
        if (this.board.isValidPosition(this.currentBlock)) { // if rotation was successful
            this.sound.playSound('rotate');
        }
    }

    dropBlock() {
        if (!this.currentBlock || this.gameOver || this.paused) return;
        let landed = false;
        while (this.board.isValidPosition(this.currentBlock)) {
            this.currentBlock.move(0, 1);
            landed = true;
        }
        this.currentBlock.move(0, -1); // Move back one step to valid position
        if (landed) { // Play drop sound only if it actually moved
            this.sound.playSound('drop');
        }
        this.placeBlock();
    }

    updateScore(clearedLines) {
        if (clearedLines > 0 && clearedLines < this.lineClearPoints.length) {
            this.score += this.lineClearPoints[clearedLines] * this.level;
        }
    }

    updateLevel() {
        const newLevel = Math.floor(this.linesCleared / 10) + 1;
        if (newLevel > this.level) {
            this.level = newLevel;
            this.updateFallSpeed();
        }
    }

    updateFallSpeed() {
        this.fallSpeed = Math.max(100, 1000 - (this.level - 1) * 50); // Decrease speed, min 100ms
    }

    togglePause() {
        this.paused = !this.paused;
        if (this.paused) {
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = 'Paused. Press P to Resume.';
            }
            this.sound.stopBackgroundMusic();
        } else {
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = ''; // Clear pause message
            }
            this.lastFallTime = performance.now();
            if (!this.gameOver) {
                this.sound.startBackgroundMusic();
                this.gameLoop(performance.now());
            }
        }
    }

    restartGame() {
        this.sound.stopBackgroundMusic(); // Stop any previous music
        this.init();
        this.sound.startBackgroundMusic(); // Start fresh
        this.gameLoop();
    }

    updateDisplays() {
        if (this.scoreDisplay) this.scoreDisplay.textContent = this.score;
        if (this.levelDisplay) this.levelDisplay.textContent = this.level;
        if (this.linesDisplay) this.linesDisplay.textContent = this.linesCleared;
    }

    // --- Rendering Methods ---

    draw() {
        // Clear main canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw board (grid and placed blocks)
        this.drawBoard(this.ctx);

        // Draw current block and ghost block if the game is active
        if (this.currentBlock && !this.gameOver && !this.paused) {
            this.drawGhostBlock(this.ctx);
            this.drawBlock(this.currentBlock, this.ctx, this.currentBlock.color, false); // Pass actual color
        }
        // updateDisplays is already called when score/level/lines change.
        // If not, it could be called here as well.
        // this.updateDisplays();
    }

    drawBoard(context) {
        context.strokeStyle = '#111'; // Darker grid lines
        context.lineWidth = 1;

        for (let y = 0; y < Board.HEIGHT; y++) {
            for (let x = 0; x < Board.WIDTH; x++) {
                const cellX = x * Board.CELL_SIZE;
                const cellY = y * Board.CELL_SIZE;

                if (this.board.grid[y][x]) {
                    context.fillStyle = this.board.grid[y][x]; // Color from placed block
                    context.fillRect(cellX, cellY, Board.CELL_SIZE, Board.CELL_SIZE);
                    context.strokeRect(cellX, cellY, Board.CELL_SIZE, Board.CELL_SIZE); // Border for filled cell
                } else {
                    // Optional: Draw empty cells if you want a visible grid
                    // context.fillStyle = '#eee'; // Very light gray for empty cells
                    // context.fillRect(cellX, cellY, Board.CELL_SIZE, Board.CELL_SIZE);
                    context.strokeRect(cellX, cellY, Board.CELL_SIZE, Board.CELL_SIZE); // Border for empty cell
                }
            }
        }
    }

    /**
     * Draws a block on the given canvas context.
     * @param {Block} block The block to draw.
     * @param {CanvasRenderingContext2D} context The context to draw on.
     * @param {string} color The color to draw the block. Can be overridden for ghost block.
     * @param {boolean} isGhost Indicates if the block is a ghost block for styling.
     * @param {number} [customOffsetX=0] Optional X offset in grid cells.
     * @param {number} [customOffsetY=0] Optional Y offset in grid cells.
     */
    drawBlock(block, context, color, isGhost, customOffsetX = 0, customOffsetY = 0) {
        if (!block) return;

        context.fillStyle = color;
        if (isGhost) {
            context.globalAlpha = 0.3; // Semi-transparent for ghost
        } else {
            context.globalAlpha = 1.0; // Fully opaque for regular blocks
        }

        const cellSize = Board.CELL_SIZE; // Use the global cell size

        for (let r = 0; r < block.shape.length; r++) {
            for (let c = 0; c < block.shape[r].length; c++) {
                if (block.shape[r][c]) {
                    const drawX = (block.x + c + customOffsetX) * cellSize;
                    const drawY = (block.y + r + customOffsetY) * cellSize;

                    context.fillRect(drawX, drawY, cellSize, cellSize);

                    if (!isGhost) {
                        context.strokeStyle = '#333'; // Darker border for each cell of the block
                        context.lineWidth = 1;
                        context.strokeRect(drawX, drawY, cellSize, cellSize);
                    }
                }
            }
        }
        context.globalAlpha = 1.0; // Reset alpha
    }

    drawGhostBlock(context) {
        if (!this.currentBlock) return;

        // Create a temporary copy of the current block to simulate its fall
        const ghostBlockCopy = new Block(
            this.currentBlock.shape, // Keep the same shape
            this.currentBlock.color, // Use the block's actual color, drawBlock will handle transparency
            this.currentBlock.x,
            this.currentBlock.y
        );

        // Move the copy down until it hits an obstacle or the bottom
        while (this.board.isValidPosition(ghostBlockCopy)) {
            ghostBlockCopy.y++;
        }
        ghostBlockCopy.y--; // Move back one step to the last valid position

        // Draw the ghost block using the main drawBlock method with a ghost flag
        this.drawBlock(ghostBlockCopy, context, 'grey', true); // Use 'grey' or a specific ghost color
    }


    drawNextBlock() {
        this.nextBlockCtx.clearRect(0, 0, this.nextBlockCanvas.width, this.nextBlockCanvas.height);
        if (this.nextBlock) {
            const block = this.nextBlock;
            const ctx = this.nextBlockCtx;
            const cellSize = Board.CELL_SIZE; // Use consistent cell size

            // Calculate offsets to center the block in the nextBlockCanvas (assuming 4x4 cell area)
            const canvasCellWidth = this.nextBlockCanvas.width / cellSize;
            const canvasCellHeight = this.nextBlockCanvas.height / cellSize;

            const shapeWidth = block.shape[0].length;
            const shapeHeight = block.shape.length;

            // Center based on the shape's dimensions
            const offsetX = (canvasCellWidth - shapeWidth) / 2;
            const offsetY = (canvasCellHeight - shapeHeight) / 2;

            // Temporarily adjust block's own x and y for drawing logic if drawBlock expects them to be 0 for this canvas
            const originalBlockX = block.x;
            const originalBlockY = block.y;
            block.x = 0; // Set to 0,0 as reference for drawing within nextBlockCanvas
            block.y = 0;

            this.drawBlock(block, ctx, block.color, false, offsetX, offsetY);

            // Restore original x, y if they were changed
            block.x = originalBlockX;
            block.y = originalBlockY;
        }
    }

    // --- End Rendering Methods ---


    // Method to be called to start the game
    start() {
        this.init();
        this.initEventListeners();
        this.sound.startBackgroundMusic(); // Start music when game starts
        this.gameLoop();
    }

    initEventListeners() {
        // Add a one-time event listener for the first user interaction to resume AudioContext
        const firstInteractionListener = () => {
            if (this.sound && this.sound.audioContext && this.sound.audioContext.state === 'suspended') {
                this.sound.resumeAudioContext();
            }
            this.userInteracted = true; // Mark that user has interacted
            // Optionally remove this listener if it's truly one-time for global interaction
            document.removeEventListener('keydown', firstInteractionListener, true);
            document.removeEventListener('click', firstInteractionListener, true);
        };
        // Listen for keydown or click as first interaction
        document.addEventListener('keydown', firstInteractionListener, { once: true, capture: true });
        document.addEventListener('click', firstInteractionListener, { once: true, capture: true });


        document.addEventListener('keydown', event => this.handleKeyInput(event));
    }

    handleKeyInput(event) {
        // Resume audio context on any key press if suspended (first interaction)
        if (this.sound.audioContext && this.sound.audioContext.state === 'suspended') {
            this.sound.resumeAudioContext();
        }
        this.userInteracted = true;


        // Global controls (can be used anytime)
        if (event.code === 'KeyP') {
            event.preventDefault();
            this.togglePause();
            return;
        }
        if (event.code === 'KeyR') {
            event.preventDefault();
            this.restartGame();
            return;
        }
        if (event.code === 'KeyM') {
            event.preventDefault();
            this.sound.toggleMute();
            if (this.gameMessagesElement) {
                this.gameMessagesElement.textContent = this.sound.isMuted ? "Muted" : "Sound On";
                setTimeout(() => {
                    if (this.gameMessagesElement && (this.gameMessagesElement.textContent === "Muted" || this.gameMessagesElement.textContent === "Sound On")) {
                        if(!this.gameOver && !this.paused) this.gameMessagesElement.textContent = "";
                        else if(this.paused) this.gameMessagesElement.textContent = 'Paused. Press P to Resume.';
                        // else if game over, the high score display will take over.
                    }
                }, 1500);
            }
            return;
        }
        if (event.code === 'KeyH') {
             event.preventDefault();
             if (this.gameOver) {
                 this.displayHighScores();
             }
             return;
        }
        if (event.code === 'KeyV') { // 'V' for Save (as 'S' is used for down)
            event.preventDefault();
            if (!this.gameOver && !this.paused) {
                this.saveGameState();
            }
            return;
        }
        if (event.code === 'KeyL') { // 'L' for Load
            event.preventDefault();
            // Potentially pause current game before loading, or just load over it
            this.loadGameState();
            return;
        }


        // Prevent actions if game is over or paused (specific game actions)
        // Note: KeyR (Restart) is already handled above and works in gameOver state.
        if (this.gameOver || this.paused) {
            return;
        }

        // Game controls (only when game is active)
        switch (event.code) { // Using event.code for layout-independent keys
            case 'ArrowLeft':
            case 'KeyA':
                event.preventDefault();
                this.moveBlock(-1);
                break;
            case 'ArrowRight':
            case 'KeyD':
                event.preventDefault();
                this.moveBlock(1);
                break;
            case 'ArrowDown':
            case 'KeyS':
                event.preventDefault();
                if (this.tryMoveBlock(0, 1)) { // Soft drop
                    // Reset fall timer to make soft drop responsive only if move was successful
                    this.lastFallTime = performance.now();
                }
                break;
            case 'ArrowUp':
            case 'KeyW':
            case 'KeyX':
                event.preventDefault();
                this.rotateBlock();
                break;
            case 'Space':
                event.preventDefault();
                this.dropBlock(); // Hard drop
                break;
            // No default case needed, allows other keys for browser functions
        }
    }

    // Setter for game messages element (if needed later)
    setGameMessagesElement(element) {
        this.gameMessagesElement = element;
    }
}
