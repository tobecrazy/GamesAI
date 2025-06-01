class Sound {
    constructor() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.error("Web Audio API is not supported in this browser.", e);
            // Fallback or disable sound if AudioContext is not supported
            this.audioContext = null;
        }
        this.sounds = {};
        this.isMuted = false;
        this.backgroundMusicElement = null; // Will be an <audio> element
        this.backgroundMusicSourceNode = null; // For controlling connected background music
    }

    async loadSound(name, path) {
        if (!this.audioContext) return; // Don't load if AudioContext failed

        try {
            const response = await fetch(path);
            if (!response.ok) {
                throw new Error(`Failed to fetch sound: ${path}, status: ${response.status}`);
            }
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            this.sounds[name] = audioBuffer;
            console.log(`Sound loaded: ${name} from ${path}`);
        } catch (error) {
            console.error(`Error loading sound ${name} from ${path}:`, error);
        }
    }

    playSound(name) {
        if (!this.audioContext || this.isMuted || !this.sounds[name]) {
            if (!this.sounds[name] && name !== 'background') { // Don't warn for background not being in this.sounds
                console.warn(`Sound not found or not loaded: ${name}`);
            }
            return;
        }

        const source = this.audioContext.createBufferSource();
        source.buffer = this.sounds[name];
        source.connect(this.audioContext.destination);
        source.start(0);
    }

    initBackgroundMusic(path) {
        if (this.backgroundMusicElement) { // If already initialized, stop and remove old one
            this.backgroundMusicElement.pause();
            this.backgroundMusicElement.remove();
        }

        this.backgroundMusicElement = new Audio(path);
        this.backgroundMusicElement.loop = true;
        this.backgroundMusicElement.preload = 'auto';

        // Optional: Connect to AudioContext if advanced processing is needed later
        // However, for simple play/pause/loop, direct <audio> element is often easier.
        // If you want to apply AudioContext effects (e.g. gain), you'd use a MediaElementAudioSourceNode.
        // For now, we'll control it directly.
    }

    startBackgroundMusic() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                console.log("AudioContext resumed by user interaction.");
                this._playBgMusic();
            }).catch(e => console.error("Error resuming AudioContext:", e));
        } else {
            this._playBgMusic();
        }
    }

    _playBgMusic() {
         if (this.backgroundMusicElement && !this.isMuted) {
            this.backgroundMusicElement.play().catch(error => {
                // Autoplay was prevented, common issue.
                // User interaction is typically required to start audio.
                console.warn("Background music play prevented:", error);
                // We might need a UI element (e.g. "Click to enable sound")
                // or rely on the first game interaction to enable it.
            });
        }
    }


    stopBackgroundMusic() {
        if (this.backgroundMusicElement) {
            this.backgroundMusicElement.pause();
        }
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        if (this.isMuted) {
            this.stopBackgroundMusic();
             if (this.audioContext && this.backgroundMusicSourceNode) {
                // If using AudioBufferSourceNode for bg music, you'd stop it.
                // this.backgroundMusicSourceNode.stop();
            }
        } else {
            this.startBackgroundMusic();
        }
        console.log(`Mute toggled. Is muted: ${this.isMuted}`);
        return this.isMuted;
    }

    // Call this on first user interaction to enable audio if needed
    resumeAudioContext() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                console.log("AudioContext resumed successfully.");
                // If background music was supposed to play, try starting it again
                if (!this.isMuted && this.backgroundMusicElement && this.backgroundMusicElement.paused) {
                    this.startBackgroundMusic();
                }
            }).catch(e => console.error("Error resuming AudioContext:", e));
        }
    }
}
