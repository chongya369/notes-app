const API_BASE_URL = '';

let token = localStorage.getItem('token') || '';
let currentUsername = localStorage.getItem('username') || '';
let editingNoteId = null;
const saveTimeouts = {};
let sortable = null;

const authPage = document.getElementById('auth-page');
const mainPage = document.getElementById('main-page');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const tabBtns = document.querySelectorAll('.tab-btn');
const notesContainer = document.getElementById('notes-container');
const createModal = document.getElementById('create-modal');
const usernameDisplay = document.getElementById('username-display');

document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        showMainPage();
        loadNotes();
    } else {
        showAuthPage();
    }
});

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const tab = btn.dataset.tab;
        if (tab === 'login') {
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        } else {
            registerForm.classList.add('active');
            loginForm.classList.remove('active');
        }
    });
});

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const username = formData.get('username');
    const password = formData.get('password');

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            token = data.access_token;
            currentUsername = username;
            localStorage.setItem('token', token);
            localStorage.setItem('username', currentUsername);
            showMainPage();
            loadNotes();
            loginForm.reset();
        } else {
            alert(data.detail || '登录失败');
        }
    } catch (error) {
        alert('网络错误，请检查后端服务是否启动');
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const username = formData.get('username');
    const password = formData.get('password');
    const key = formData.get('key');

    const body = { username, password };
    if (key && key.trim()) {
        body.key = key.trim();
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            alert('注册成功，请登录');
            tabBtns[0].click();
            registerForm.reset();
        } else {
            alert(data.detail || '注册失败');
        }
    } catch (error) {
        alert('网络错误，请检查后端服务是否启动');
    }
});

document.getElementById('logout-btn').addEventListener('click', () => {
    token = '';
    currentUsername = '';
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    showAuthPage();
});

document.getElementById('create-note-btn').addEventListener('click', () => {
    document.getElementById('new-note-content').value = '';
    document.getElementById('new-note-color').value = '#FFE4B5';
    createModal.classList.remove('hidden');
});

document.getElementById('save-new-btn').addEventListener('click', async () => {
    const content = document.getElementById('new-note-content').value.trim();
    const color = document.getElementById('new-note-color').value;

    if (!content) {
        alert('请输入便签内容');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ content, color })
        });

        const data = await response.json();

        if (response.ok) {
            createModal.classList.add('hidden');
            loadNotes();
        } else {
            alert(data.detail || '创建失败');
        }
    } catch (error) {
        alert('网络错误');
    }
});

document.getElementById('cancel-create-btn').addEventListener('click', () => {
    createModal.classList.add('hidden');
});

async function loadNotes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/notes`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const notes = await response.json();

        if (response.ok) {
            renderNotes(notes);
        } else {
            if (response.status === 401) {
                alert('认证失败，请重新登录');
                showAuthPage();
            } else {
                alert('加载失败');
            }
        }
    } catch (error) {
        alert('网络错误');
    }
}

function renderNotes(notes) {
    notesContainer.innerHTML = '';

    if (notes.length === 0) {
        notesContainer.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">暂无便签，请创建第一条便签</p>';
        return;
    }

    notes.forEach(note => {
        const noteCard = document.createElement('div');
        noteCard.className = 'note-card';
        noteCard.style.background = note.color;

        const title = note.title || '';
        const content = note.content || '';
        const updatedAt = new Date(note.updated_at).toLocaleString('zh-CN');

        noteCard.dataset.id = note.id;

        noteCard.innerHTML = `
            <div class="drag-handle" title="拖动排序">⋮⋮</div>
            <textarea class="note-content-edit" placeholder="输入便签内容...">${escapeHtml(content)}</textarea>
            <div class="note-footer">
                <div class="note-time">${updatedAt}</div>
                <div class="note-actions">
                    <span class="note-status saved" data-status="saved">已保存</span>
                    <button class="note-btn delete-btn" data-id="${note.id}">删除</button>
                </div>
            </div>
        `;

        notesContainer.appendChild(noteCard);
    });

    bindNoteEvents();
    initSortable();
}

function bindNoteEvents() {
    document.querySelectorAll('.note-card').forEach(card => {
        const contentInput = card.querySelector('.note-content-edit');

        if (contentInput) {
            contentInput.addEventListener('input', () => onNoteInput(card));
        }
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteNote(btn.dataset.id);
        });
    });

    document.querySelectorAll('.note-status.error').forEach(status => {
        status.addEventListener('click', (e) => {
            e.stopPropagation();
            const card = status.closest('.note-card');
            triggerSave(card);
        });
    });
}

function initSortable() {
    if (sortable) {
        sortable.destroy();
    }

    if (window.Sortable) {
        sortable = new Sortable(notesContainer, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            
            onEnd: async function(evt) {
                const noteIds = Array.from(notesContainer.children)
                    .map(card => parseInt(card.dataset.id));
                
                try {
                    await fetch(`${API_BASE_URL}/api/notes/sort`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(noteIds)
                    });
                } catch (error) {
                    console.error('排序保存失败:', error);
                    loadNotes();
                }
            }
        });
    }
}

function setNoteStatus(card, status, message) {
    const statusEl = card.querySelector('.note-status');
    if (!statusEl) return;

    statusEl.className = `note-status ${status}`;
    statusEl.dataset.status = status;
    
    const messages = {
        'editing': '正在输入...',
        'saving': '正在保存...',
        'saved': '已保存',
        'error': message || '保存失败，点击重试'
    };
    statusEl.textContent = messages[status] || message || status;

    if (status === 'saved') {
        setTimeout(() => {
            if (card.querySelector('.note-status')?.dataset.status === 'saved') {
                card.querySelector('.note-status').textContent = '';
            }
        }, 3000);
    }
}

function onNoteInput(card) {
    const noteId = card.dataset.id;

    if (saveTimeouts[noteId]) {
        clearTimeout(saveTimeouts[noteId]);
    }

    setNoteStatus(card, 'editing');

    saveTimeouts[noteId] = setTimeout(() => {
        triggerSave(card);
    }, 1500);
}

async function triggerSave(card) {
    const noteId = card.dataset.id;
    if (!noteId) return;

    const contentInput = card.querySelector('.note-content-edit');

    if (!contentInput) return;

    const content = contentInput.value.trim();

    setNoteStatus(card, 'saving');

    try {
        const response = await fetch(`${API_BASE_URL}/api/notes/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            const note = await response.json();
            setNoteStatus(card, 'saved');

            const timeEl = card.querySelector('.note-time');
            if (timeEl) {
                timeEl.textContent = new Date(note.updated_at).toLocaleString('zh-CN');
            }
        } else {
            const data = await response.json();
            setNoteStatus(card, 'error', data.detail || '保存失败');
        }
    } catch (error) {
        setNoteStatus(card, 'error', '网络错误');
    }
}

async function deleteNote(noteId) {
    if (!confirm('确定要删除这条便签吗？')) {
        return;
    }

    if (saveTimeouts[noteId]) {
        clearTimeout(saveTimeouts[noteId]);
        delete saveTimeouts[noteId];
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/notes/${noteId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            loadNotes();
        } else {
            const data = await response.json();
            alert(data.detail || '删除失败');
        }
    } catch (error) {
        alert('网络错误');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function showAuthPage() {
    authPage.classList.remove('hidden');
    mainPage.classList.add('hidden');
}

function showMainPage() {
    authPage.classList.add('hidden');
    mainPage.classList.remove('hidden');
    usernameDisplay.textContent = `用户: ${currentUsername}`;
}
