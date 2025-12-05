/**
 * Swipe Module - Handles touch/mouse gestures for card swiping
 */

class SwipeHandler {
    constructor(element, callbacks = {}) {
        this.element = element;
        this.callbacks = {
            onSwipeLeft: callbacks.onSwipeLeft || (() => { }),
            onSwipeRight: callbacks.onSwipeRight || (() => { }),
            onSwipeUp: callbacks.onSwipeUp || (() => { }),
            onMove: callbacks.onMove || (() => { }),
            onRelease: callbacks.onRelease || (() => { })
        };

        this.startX = 0;
        this.startY = 0;
        this.currentX = 0;
        this.currentY = 0;
        this.isDragging = false;

        this.SWIPE_THRESHOLD = 100;
        this.ROTATION_FACTOR = 0.1;

        this.bindEvents();
    }

    bindEvents() {
        // Mouse events
        this.element.addEventListener('mousedown', this.handleStart.bind(this));
        document.addEventListener('mousemove', this.handleMove.bind(this));
        document.addEventListener('mouseup', this.handleEnd.bind(this));

        // Touch events
        this.element.addEventListener('touchstart', this.handleStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleEnd.bind(this));
    }

    getEventPosition(e) {
        if (e.touches && e.touches.length > 0) {
            return { x: e.touches[0].clientX, y: e.touches[0].clientY };
        }
        return { x: e.clientX, y: e.clientY };
    }

    handleStart(e) {
        if (e.target.closest('.action-btn')) return;

        const pos = this.getEventPosition(e);
        this.startX = pos.x;
        this.startY = pos.y;
        this.isDragging = true;

        this.element.classList.add('dragging');
        this.element.style.transition = 'none';
    }

    handleMove(e) {
        if (!this.isDragging) return;

        e.preventDefault();

        const pos = this.getEventPosition(e);
        this.currentX = pos.x - this.startX;
        this.currentY = pos.y - this.startY;

        const rotation = this.currentX * this.ROTATION_FACTOR;
        const opacity = 1 - Math.abs(this.currentX) / 500;

        this.element.style.transform = `translateX(${this.currentX}px) translateY(${this.currentY}px) rotate(${rotation}deg)`;

        // Update swipe indicator classes
        this.element.classList.remove('swiping-left', 'swiping-right');

        if (this.currentX > 50) {
            this.element.classList.add('swiping-right');
        } else if (this.currentX < -50) {
            this.element.classList.add('swiping-left');
        }

        this.callbacks.onMove(this.currentX, this.currentY);
    }

    handleEnd(e) {
        if (!this.isDragging) return;

        this.isDragging = false;
        this.element.classList.remove('dragging');
        this.element.style.transition = '';

        const absX = Math.abs(this.currentX);
        const absY = Math.abs(this.currentY);

        if (absX > this.SWIPE_THRESHOLD && absX > absY) {
            // Horizontal swipe
            if (this.currentX > 0) {
                this.callbacks.onSwipeRight();
            } else {
                this.callbacks.onSwipeLeft();
            }
        } else if (this.currentY < -this.SWIPE_THRESHOLD && absY > absX) {
            // Upward swipe
            this.callbacks.onSwipeUp();
        } else {
            // Reset position
            this.element.style.transform = '';
            this.element.classList.remove('swiping-left', 'swiping-right');
            this.callbacks.onRelease();
        }

        this.currentX = 0;
        this.currentY = 0;
    }

    // Programmatic swipe methods
    swipeLeft() {
        this.animateOut('left');
        this.callbacks.onSwipeLeft();
    }

    swipeRight() {
        this.animateOut('right');
        this.callbacks.onSwipeRight();
    }

    swipeUp() {
        this.animateOut('up');
        this.callbacks.onSwipeUp();
    }

    animateOut(direction) {
        this.element.classList.add(`exit-${direction}`);
    }

    destroy() {
        this.element.removeEventListener('mousedown', this.handleStart);
        this.element.removeEventListener('touchstart', this.handleStart);
        document.removeEventListener('mousemove', this.handleMove);
        document.removeEventListener('touchmove', this.handleMove);
        document.removeEventListener('mouseup', this.handleEnd);
        document.removeEventListener('touchend', this.handleEnd);
    }
}
