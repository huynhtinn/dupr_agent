/**
 * DUPR Chatbot - Enhanced Interactions
 * Version 2.0 - Professional UI/UX
 */

class DUPRChatbot {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.setupThemeToggle();
    }

    init() {
        console.log('🏓 DUPR Chatbot initialized');
        this.detectSystemTheme();
        this.addWelcomeMessage();
        this.setupTypingIndicator();
        this.enhanceSourceChips();
    }

    detectSystemTheme() {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.classList.add('dark');
        }
    }

    setupThemeToggle() {
        window.toggleDark = (isDark) => {
            document.documentElement.classList.toggle('dark', !!isDark);
            
            // Save theme preference
            localStorage.setItem('dupr-theme', isDark ? 'dark' : 'light');
            
            // Show toast notification
            this.showToast(isDark ? '🌙 Đã chuyển sang chế độ tối' : '☀️ Đã chuyển sang chế độ sáng', 'info');
        };

        // Load saved theme
        const savedTheme = localStorage.getItem('dupr-theme');
        if (savedTheme) {
            document.documentElement.classList.toggle('dark', savedTheme === 'dark');
        }
    }

    setupEventListeners() {
        // Enhanced send button click effect
        document.addEventListener('click', (e) => {
            if (e.target.matches('.gr-button')) {
                this.addRippleEffect(e.target, e);
            }
        });

        // Auto-resize textarea
        document.addEventListener('input', (e) => {
            if (e.target.matches('textarea')) {
                this.autoResizeTextarea(e.target);
            }
        });

        // Smooth scroll for new messages
        this.observeChatMessages();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const sendButton = document.querySelector('.gr-button[variant="primary"]');
                if (sendButton) {
                    sendButton.click();
                    this.showToast('📤 Tin nhắn đã được gửi!', 'success');
                }
            }

            // Ctrl/Cmd + K to clear chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const clearButton = document.querySelector('.gr-button:not([variant="primary"])');
                if (clearButton && clearButton.textContent.includes('Xóa')) {
                    clearButton.click();
                    this.showToast('🗑️ Đã xóa lịch sử chat!', 'info');
                }
            }
        });
    }

    addRippleEffect(button, event) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    observeChatMessages() {
        const chatContainer = document.querySelector('.gr-chatbot');
        if (!chatContainer) return;

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    this.scrollToBottom(chatContainer);
                    this.animateNewMessage(mutation.addedNodes);
                }
            });
        });

        observer.observe(chatContainer, {
            childList: true,
            subtree: true
        });
    }

    scrollToBottom(container) {
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
    }

    animateNewMessage(nodes) {
        nodes.forEach(node => {
            if (node.nodeType === 1 && node.classList) {
                node.style.opacity = '0';
                node.style.transform = 'translateY(20px)';
                
                requestAnimationFrame(() => {
                    node.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                    node.style.opacity = '1';
                    node.style.transform = 'translateY(0)';
                });
            }
        });
    }

    setupTypingIndicator() {
        this.typingIndicator = document.createElement('div');
        this.typingIndicator.className = 'typing-indicator';
        this.typingIndicator.innerHTML = `
            <span>💭 Đang suy nghĩ</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        this.typingIndicator.style.display = 'none';
    }

    showTyping() {
        const chatContainer = document.querySelector('.gr-chatbot');
        if (chatContainer && this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            chatContainer.appendChild(this.typingIndicator);
            this.scrollToBottom(chatContainer);
        }
    }

    hideTyping() {
        if (this.typingIndicator && this.typingIndicator.parentNode) {
            this.typingIndicator.parentNode.removeChild(this.typingIndicator);
        }
    }

    enhanceSourceChips() {
        // Enhance source chips with better interactions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.source-chip, .source-chip *')) {
                const chip = e.target.closest('.source-chip');
                if (chip) {
                    this.handleSourceChipClick(chip);
                }
            }
        });
    }

    handleSourceChipClick(chip) {
        // Add visual feedback
        chip.style.transform = 'scale(0.95)';
        setTimeout(() => {
            chip.style.transform = '';
        }, 150);

        // Extract source info and show details
        const sourceText = chip.textContent;
        this.showToast(`📖 Đã chọn nguồn: ${sourceText}`, 'info');
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: currentColor; cursor: pointer; padding: 0; margin-left: auto;">✕</button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutToRight 0.3s ease-out forwards';
                setTimeout(() => toast.remove(), 300);
            }
        }, 3000);
    }

    addWelcomeMessage() {
        // Add a subtle welcome animation
        setTimeout(() => {
            const header = document.querySelector('.header-card');
            if (header) {
                header.style.animation = 'fadeInUp 0.8s ease-out';
            }
        }, 100);
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Additional CSS animations
const additionalStyles = `
@keyframes ripple {
    from {
        transform: scale(0);
        opacity: 1;
    }
    to {
        transform: scale(2);
        opacity: 0;
    }
}

@keyframes slideOutToRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.typing-dots {
    display: flex;
    gap: 2px;
    margin-left: 8px;
}

.typing-indicator {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background: rgba(79, 70, 229, 0.1);
    border-radius: 16px;
    margin: 8px 0;
    color: #4f46e5;
    font-size: 14px;
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new DUPRChatbot());
} else {
    new DUPRChatbot();
}

// Export for global access
window.DUPRChatbot = DUPRChatbot;
