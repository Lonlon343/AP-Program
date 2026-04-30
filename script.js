document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded and ready.');
});

/**
 * Example function to demonstrate basic functionality
 * @param {string} message - The message to display
 */
function displayMessage(message) {
    const outputElement = document.getElementById('output');
    if (outputElement) {
        outputElement.textContent = message;
    } else {
        console.log(message);
    }
}

/**
 * Adds micro-animations to elements with the 'animate-hover' class
 */
function initMicroAnimations() {
    const animatedElements = document.querySelectorAll('.animate-hover, button, img');

    animatedElements.forEach(element => {
        element.style.transition = 'transform 0.2s ease-in-out, filter 0.2s ease-in-out';

        element.addEventListener('mouseenter', () => {
            element.style.transform = 'scale(1.05)';
            element.style.filter = 'brightness(1.1)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'scale(1)';
            element.style.filter = 'brightness(1)';
        });

        element.addEventListener('mousedown', () => {
            element.style.transform = 'scale(0.95)';
        });

        element.addEventListener('mouseup', () => {
            element.style.transform = 'scale(1.05)';
        });
    });
}

// Initialize animations when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initMicroAnimations);

// Create wave-like animated background with geometry
function initWaveBackground() {
    // Generate keyframes for waveFlow with every percent
    let waveKeyframes = '';
    for (let i = 0; i <= 100; i++) {
        const pos = 50 + 50 * Math.sin((i / 100) * 2 * Math.PI);
        waveKeyframes += `${i}% { background-position: ${pos}% 50%; }\n`;
    }

    // Generate keyframes for float with every percent
    let floatKeyframes = '';
    for (let i = 0; i <= 100; i++) {
        const y = -20 * Math.sin((i / 100) * 2 * Math.PI);
        const rot = 360 * (i / 100);
        floatKeyframes += `${i}% { transform: translateY(${y}px) rotate(${rot}deg); }\n`;
    }

    const style = document.createElement('style');
    style.textContent = `
        @keyframes waveFlow {
            ${waveKeyframes}
        }
        body {
            background: linear-gradient(45deg, #1e3a8a, #3b82f6, #06b6d4, #8b5cf6, #1e40af);
            background-size: 400% 400%;
            animation: waveFlow 4s ease-in-out infinite;
            position: relative;
            overflow: auto;
        }
        .geo-shape {
            position: absolute;
            border-radius: 50%;
            background: rgba(59, 130, 246, 0.3);
            animation: float 6s ease-in-out infinite;
        }
        .geo-shape:nth-child(2n) {
            border-radius: 0;
            width: 20px;
            height: 20px;
            background: rgba(6, 182, 212, 0.3);
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
        }
        @keyframes float {
            ${floatKeyframes}
        }
    `;
    document.head.appendChild(style);

    // Add geometric shapes
    for (let i = 0; i < 10; i++) {
        const shape = document.createElement('div');
        shape.className = 'geo-shape';
        shape.style.left = Math.random() * 100 + '%';
        shape.style.top = Math.random() * 100 + '%';
        shape.style.width = (Math.random() * 50 + 20) + 'px';
        shape.style.height = shape.style.width;
        shape.style.animationDelay = Math.random() * 6 + 's';
        document.body.appendChild(shape);
    }
}

// Initialize wave background when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initWaveBackground);

// --- Improved Net and Responsive Styling ---
function updateGeoShapeStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .geo-shape {
            border: 2px solid #fff;
            box-shadow: 0 4px 24px 0 rgba(59,130,246,0.25), 0 1.5px 6px 0 rgba(139,92,246,0.15);
            transition: box-shadow 0.3s, border-color 0.3s;
            background-blend-mode: lighten;
            backdrop-filter: blur(2px);
        }
        .geo-shape:hover {
            border-color: #06b6d4;
            box-shadow: 0 8px 32px 0 rgba(6,182,212,0.35), 0 2px 8px 0 rgba(139,92,246,0.25);
            z-index: 2;
        }
    `;
    document.head.appendChild(style);
}
document.addEventListener('DOMContentLoaded', updateGeoShapeStyles);

function initDynamicNetAndStatic() {
    const canvas = document.getElementById('net-static-canvas') || document.createElement('canvas');
    canvas.id = 'net-static-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = 0;
    canvas.style.left = 0;
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = 0;
    if (!canvas.parentNode) document.body.prepend(canvas);

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    let mouse = { x: null, y: null, active: false };
    document.addEventListener('mousemove', e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    document.addEventListener('mouseenter', e => { mouse.active = true; });
    document.addEventListener('mouseleave', e => { mouse.active = false; });
    canvas.addEventListener('mouseenter', e => { mouse.active = true; });
    canvas.addEventListener('mouseleave', e => { mouse.active = false; });

    function getShapeCenters() {
        const shapes = Array.from(document.querySelectorAll('.geo-shape'));
        return shapes.map(shape => {
            const rect = shape.getBoundingClientRect();
            return {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            };
        });
    }

    function drawNet(ctx, centers) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255,255,255,0.18)';
        ctx.lineWidth = 1.5;
        for (let i = 0; i < centers.length; i++) {
            for (let j = i + 1; j < centers.length; j++) {
                ctx.beginPath();
                ctx.moveTo(centers[i].x, centers[i].y);
                ctx.lineTo(centers[j].x, centers[j].y);
                ctx.stroke();
            }
        }
        // Draw lines from mouse to all shapes if mouse is active
        if (mouse.x !== null && mouse.y !== null && mouse.active) {
            ctx.strokeStyle = 'rgba(6,182,212,0.35)';
            ctx.lineWidth = 2.5;
            centers.forEach(center => {
                ctx.beginPath();
                ctx.moveTo(mouse.x, mouse.y);
                ctx.lineTo(center.x, center.y);
                ctx.stroke();
            });
        }
        ctx.restore();
    }

    function drawStatic(ctx) {
        const w = canvas.width, h = canvas.height;
        const imageData = ctx.createImageData(w, h);
        for (let i = 0; i < w * h * 4; i += 4) {
            const shade = Math.random() * 255;
            imageData.data[i] = shade;
            imageData.data[i + 1] = shade;
            imageData.data[i + 2] = shade;
            imageData.data[i + 3] = Math.random() < 0.08 ? 32 : 0; // sparse static
        }
        ctx.putImageData(imageData, 0, 0);
    }

    function animate() {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawStatic(ctx);
        const centers = getShapeCenters();
        drawNet(ctx, centers);
        requestAnimationFrame(animate);
    }
    animate();
}
document.addEventListener('DOMContentLoaded', initDynamicNetAndStatic);

// --- Net Game Logic ---
function initNetGame() {
    let score = 0;
    let totalShapes = 0;
    let gameOver = false;
    // Score display
    const scoreDiv = document.createElement('div');
    scoreDiv.id = 'net-game-score';
    scoreDiv.style.position = 'fixed';
    scoreDiv.style.top = '24px';
    scoreDiv.style.right = '32px';
    scoreDiv.style.zIndex = 1000;
    scoreDiv.style.fontSize = '2rem';
    scoreDiv.style.fontWeight = 'bold';
    scoreDiv.style.color = '#06b6d4';
    scoreDiv.style.textShadow = '0 2px 8px #0008';
    scoreDiv.style.pointerEvents = 'none';
    scoreDiv.textContent = 'Score: 0';
    document.body.appendChild(scoreDiv);

    // Win message
    const winDiv = document.createElement('div');
    winDiv.id = 'net-game-win';
    winDiv.style.position = 'fixed';
    winDiv.style.top = '50%';
    winDiv.style.left = '50%';
    winDiv.style.transform = 'translate(-50%, -50%)';
    winDiv.style.zIndex = 1001;
    winDiv.style.fontSize = '3rem';
    winDiv.style.fontWeight = 'bold';
    winDiv.style.color = '#fff';
    winDiv.style.background = 'rgba(6,182,212,0.85)';
    winDiv.style.padding = '2rem 3rem';
    winDiv.style.borderRadius = '2rem';
    winDiv.style.boxShadow = '0 8px 32px 0 rgba(6,182,212,0.35), 0 2px 8px 0 rgba(139,92,246,0.25)';
    winDiv.style.display = 'none';
    winDiv.textContent = 'You caught all the shapes!';
    document.body.appendChild(winDiv);

    function updateScore() {
        scoreDiv.textContent = `Score: ${score}`;
    }
    function showWin() {
        winDiv.style.display = 'block';
    }
    function hideWin() {
        winDiv.style.display = 'none';
    }

    function getShapeCentersWithElements() {
        const shapes = Array.from(document.querySelectorAll('.geo-shape'));
        return shapes.map(shape => {
            const rect = shape.getBoundingClientRect();
            return {
                el: shape,
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2,
                r: Math.max(rect.width, rect.height) / 2
            };
        });
    }

    // Track mouse
    let mouse = { x: null, y: null };
    document.addEventListener('mousemove', e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    function checkCatches() {
        if (gameOver) return;
        const shapes = getShapeCentersWithElements();
        totalShapes = shapes.length;
        let caught = false;
        shapes.forEach(shape => {
            if (mouse.x !== null && mouse.y !== null) {
                const dx = shape.x - mouse.x;
                const dy = shape.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < shape.r + 24) { // 24px catch radius
                    // Explosion feedback
                    createExplosion(shape.x, shape.y, shape.isHex ? '#dc2626' : '#06b6d4');
                    // Respawn shape at top
                    shape.el.style.left = (Math.random() * 90) + '%';
                    shape.el.style.top = '-60px';
                    shape.el.dataset.speed = (Math.random() * 2.5 + 2.0).toString();
                    // 1 in 30 chance to be a hexagon
                    if (Math.random() < 1/30) {
                        shape.el.classList.add('hex-shape');
                        shape.el.style.background = 'rgba(220,38,38,0.7)';
                        shape.el.style.clipPath = 'polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)';
                        shape.el.style.border = '2px solid #b91c1c';
                        shape.el.style.boxShadow = '0 4px 24px 0 rgba(220,38,38,0.25), 0 1.5px 6px 0 rgba(220,38,38,0.15)';
                        shape.el.dataset.isHex = '1';
                    } else {
                        shape.el.classList.remove('hex-shape');
                        shape.el.style.background = 'rgba(59, 130, 246, 0.3)';
                        shape.el.style.clipPath = '';
                        shape.el.style.border = '2px solid #fff';
                        shape.el.style.boxShadow = '0 4px 24px 0 rgba(59,130,246,0.25), 0 1.5px 6px 0 rgba(139,92,246,0.15)';
                        shape.el.dataset.isHex = '0';
                    }
                    // Score logic
                    if (shape.isHex) {
                        score = Math.max(0, score - 10);
                    } else {
                        score++;
                    }
                    updateScore();
                    if (score >= scoreLimit && !gameOver) {
                        gameOver = true;
                        showWin();
                    }
                }
            }
        });
        if (totalShapes === 0 && !gameOver) {
            gameOver = true;
            showWin();
        }
    }

    function gameLoop() {
        checkCatches();
        requestAnimationFrame(gameLoop);
    }
    gameLoop();
}
// document.addEventListener('DOMContentLoaded', initNetGame); // Disabled: use falling/catching game only
document.addEventListener('DOMContentLoaded', function() {
    spawnFallingShapes(30);
    initNetGame_Falling();
});

// --- Falling Shapes and Explosion Feedback ---
function spawnFallingShapes(num = 10) {
    // Remove existing shapes
    document.querySelectorAll('.geo-shape').forEach(e => e.remove());
    for (let i = 0; i < num; i++) {
        // Every 30th shape is a red hexagon
        if ((i + 1) % 30 === 0) {
            createFallingShape(true);
        } else {
            createFallingShape(false);
        }
    }
}

function createFallingShape(isHex = false) {
    const shape = document.createElement('div');
    shape.className = 'geo-shape';
    // Randomize size and horizontal position
    const size = Math.random() * 50 + 20;
    shape.style.width = size + 'px';
    shape.style.height = size + 'px';
    shape.style.left = (Math.random() * 90) + '%';
    shape.style.top = '-60px';
    shape.style.animationDelay = Math.random() * 6 + 's';
    // Make it a red hexagon if needed
    if (isHex) {
        shape.classList.add('hex-shape');
        shape.style.background = 'rgba(220,38,38,0.7)';
        shape.style.clipPath = 'polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)';
        shape.style.border = '2px solid #b91c1c';
        shape.style.boxShadow = '0 4px 24px 0 rgba(220,38,38,0.25), 0 1.5px 6px 0 rgba(220,38,38,0.15)';
    }
    document.body.appendChild(shape);
    // Give each shape a faster random speed
    shape.dataset.speed = (Math.random() * 2.5 + 2.0).toString();
    shape.dataset.isHex = isHex ? '1' : '0';
}

// --- Performance Enhancements ---
// Cache geo-shape list for animation
let geoShapeCache = [];
let geoShapeCacheTime = 0;
function getGeoShapesCached() {
    const now = performance.now();
    if (now - geoShapeCacheTime > 100) { // update every 100ms
        geoShapeCache = Array.from(document.querySelectorAll('.geo-shape'));
        geoShapeCacheTime = now;
    }
    return geoShapeCache;
}

function animateFallingShapes() {
    const shapes = getGeoShapesCached();
    for (let i = 0; i < shapes.length; i++) {
        const shape = shapes[i];
        let top = parseFloat(shape.style.top);
        if (isNaN(top)) top = -60;
        const speed = parseFloat(shape.dataset.speed || '2');
        top += speed;
        shape.style.top = top + 'px';
        // Respawn at top if out of view
        if (top > window.innerHeight + 60) {
            if (!window.__netGameGameOver) {
                window.__netGameScore = Math.max(0, (window.__netGameScore || 0) - 5);
                if (window.__netGameUpdateScore) window.__netGameUpdateScore();
            }
            shape.style.left = (Math.random() * 90) + '%';
            shape.style.top = '-60px';
            shape.dataset.speed = (Math.random() * 2.5 + 2.0).toString();
            if (Math.random() < 1/30) {
                shape.classList.add('hex-shape');
                shape.style.background = 'rgba(220,38,38,0.7)';
                shape.style.clipPath = 'polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)';
                shape.style.border = '2px solid #b91c1c';
                shape.style.boxShadow = '0 4px 24px 0 rgba(220,38,38,0.25), 0 1.5px 6px 0 rgba(220,38,38,0.15)';
                shape.dataset.isHex = '1';
            } else {
                shape.classList.remove('hex-shape');
                shape.style.background = 'rgba(59, 130, 246, 0.3)';
                shape.style.clipPath = '';
                shape.style.border = '2px solid #fff';
                shape.style.boxShadow = '0 4px 24px 0 rgba(59,130,246,0.25), 0 1.5px 6px 0 rgba(139,92,246,0.15)';
                shape.dataset.isHex = '0';
            }
        }
    }
}

// Limit explosion particles for performance
function createExplosion(x, y, color = '#06b6d4') {
    for (let i = 0; i < 6; i++) { // was 12
        const part = document.createElement('div');
        part.className = 'explosion-part';
        part.style.position = 'fixed';
        part.style.left = x + 'px';
        part.style.top = y + 'px';
        part.style.width = '8px';
        part.style.height = '8px';
        part.style.background = color;
        part.style.borderRadius = '50%';
        part.style.pointerEvents = 'none';
        part.style.zIndex = 2000;
        part.style.opacity = 0.8;
        part.style.transform = `translate(-50%, -50%) rotate(${(360/6)*i}deg)`;
        part.style.transition = 'all 0.5s cubic-bezier(.7,1.7,.7,1)';
        document.body.appendChild(part);
        setTimeout(() => {
            part.style.transform += ` translate(${Math.random()*60+20}px, 0)`;
            part.style.opacity = 0;
        }, 10);
        setTimeout(() => part.remove(), 600);
    }
}

// Throttle getBoundingClientRect in getShapeCentersWithElements
function getShapeCentersWithElementsThrottled() {
    const now = performance.now();
    if (!getShapeCentersWithElementsThrottled.cache || now - getShapeCentersWithElementsThrottled.time > 50) {
        const shapes = getGeoShapesCached();
        getShapeCentersWithElementsThrottled.cache = shapes.map(shape => {
            const rect = shape.getBoundingClientRect();
            return {
                el: shape,
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2,
                r: Math.max(rect.width, rect.height) / 2,
                isHex: shape.dataset.isHex === '1'
            };
        });
        getShapeCentersWithElementsThrottled.time = now;
    }
    return getShapeCentersWithElementsThrottled.cache;
}

// Patch game loop to use throttled version
function initNetGame_Falling() {
    let score = 0;
    let gameOver = false;
    window.__netGameScore = score;
    window.__netGameGameOver = gameOver;
    const scoreLimit = 150;
    const scoreDiv = document.getElementById('net-game-score') || document.createElement('div');
    scoreDiv.id = 'net-game-score';
    scoreDiv.style.position = 'fixed';
    scoreDiv.style.top = '24px';
    scoreDiv.style.right = '32px';
    scoreDiv.style.zIndex = 1000;
    scoreDiv.style.fontSize = '2rem';
    scoreDiv.style.fontWeight = 'bold';
    scoreDiv.style.color = '#06b6d4';
    scoreDiv.style.textShadow = '0 2px 8px #0008';
    scoreDiv.style.pointerEvents = 'none';
    scoreDiv.textContent = 'Score: 0';
    if (!scoreDiv.parentNode) document.body.appendChild(scoreDiv);

    // Win modal with close button
    let winDiv = document.getElementById('net-game-win');
    if (!winDiv) {
        winDiv = document.createElement('div');
        winDiv.id = 'net-game-win';
        document.body.appendChild(winDiv);
    }
    winDiv.style.position = 'fixed';
    winDiv.style.top = '50%';
    winDiv.style.left = '50%';
    winDiv.style.transform = 'translate(-50%, -50%)';
    winDiv.style.zIndex = 1001;
    winDiv.style.fontSize = '3rem';
    winDiv.style.fontWeight = 'bold';
    winDiv.style.color = '#fff';
    winDiv.style.background = 'rgba(6,182,212,0.95)';
    winDiv.style.padding = '2rem 3rem';
    winDiv.style.borderRadius = '2rem';
    winDiv.style.boxShadow = '0 8px 32px 0 rgba(6,182,212,0.35), 0 2px 8px 0 rgba(139,92,246,0.25)';
    winDiv.style.display = 'none';
    winDiv.innerHTML = 'You win! Score limit reached!<br><br>';
    // Add close button
    let closeBtn = document.getElementById('net-game-close-btn');
    if (!closeBtn) {
        closeBtn = document.createElement('button');
        closeBtn.id = 'net-game-close-btn';
        closeBtn.textContent = 'Close';
        closeBtn.style.fontSize = '1.5rem';
        closeBtn.style.marginTop = '1.5rem';
        closeBtn.style.padding = '0.5rem 2rem';
        closeBtn.style.borderRadius = '1rem';
        closeBtn.style.border = 'none';
        closeBtn.style.background = '#fff';
        closeBtn.style.color = '#06b6d4';
        closeBtn.style.fontWeight = 'bold';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.boxShadow = '0 2px 8px #0003';
        winDiv.appendChild(closeBtn);
    }
    closeBtn.onclick = () => { winDiv.style.display = 'none'; };

    function updateScore() {
        scoreDiv.textContent = `Score: ${score}`;
        window.__netGameScore = score;
    }
    window.__netGameUpdateScore = updateScore;
    function showWin() {
        winDiv.style.display = 'block';
        window.__netGameGameOver = true;
    }
    function hideWin() {
        winDiv.style.display = 'none';
        window.__netGameGameOver = false;
    }

    let mouse = { x: null, y: null };
    document.addEventListener('mousemove', e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    function checkCatches() {
        if (gameOver) return;
        const shapes = getShapeCentersWithElementsThrottled();
        for (let i = 0; i < shapes.length; i++) {
            const shape = shapes[i];
            if (mouse.x !== null && mouse.y !== null) {
                const dx = shape.x - mouse.x;
                const dy = shape.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < shape.r + 24) {
                    createExplosion(shape.x, shape.y, shape.isHex ? '#dc2626' : '#06b6d4');
                    shape.el.style.left = (Math.random() * 90) + '%';
                    shape.el.style.top = '-60px';
                    shape.el.dataset.speed = (Math.random() * 2.5 + 2.0).toString();
                    if (Math.random() < 1/30) {
                        shape.el.classList.add('hex-shape');
                        shape.el.style.background = 'rgba(220,38,38,0.7)';
                        shape.el.style.clipPath = 'polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%)';
                        shape.el.style.border = '2px solid #b91c1c';
                        shape.el.style.boxShadow = '0 4px 24px 0 rgba(220,38,38,0.25), 0 1.5px 6px 0 rgba(220,38,38,0.15)';
                        shape.el.dataset.isHex = '1';
                    } else {
                        shape.el.classList.remove('hex-shape');
                        shape.el.style.background = 'rgba(59, 130, 246, 0.3)';
                        shape.el.style.clipPath = '';
                        shape.el.style.border = '2px solid #fff';
                        shape.el.style.boxShadow = '0 4px 24px 0 rgba(59,130,246,0.25), 0 1.5px 6px 0 rgba(139,92,246,0.15)';
                        shape.el.dataset.isHex = '0';
                    }
                    if (shape.isHex) {
                        score = Math.max(0, score - 10);
                    } else {
                        score++;
                    }
                    updateScore();
                    if (score >= scoreLimit && !gameOver) {
                        gameOver = true;
                        showWin();
                    }
                }
            }
        }
    }

    function gameLoop() {
        animateFallingShapes();
        checkCatches();
        requestAnimationFrame(gameLoop);
    }
    gameLoop();
}

