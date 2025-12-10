const valueInput = document.getElementById('valueInput');
const insertBtn = document.getElementById('insertBtn');
const lookupBtn = document.getElementById('lookupBtn');
const statusArea = document.getElementById('statusArea');

function setStatus(message, variant = 'ok') {
  statusArea.textContent = message;
  statusArea.classList.remove('ok', 'error');
  statusArea.classList.add(variant);
}

async function handleInsert() {
  const value = valueInput.value.trim();
  const result = await window.electronAPI.insert(value);
  if (result.ok) {
    setStatus(result.message, 'ok');
  } else {
    setStatus(result.message, 'error');
  }
}

async function handleLookup() {
  const value = valueInput.value.trim();
  const result = await window.electronAPI.lookup(value);
  if (result.ok) {
    setStatus(result.message, result.exists ? 'ok' : 'error');
  } else {
    setStatus(result.message, 'error');
  }
}

insertBtn.addEventListener('click', handleInsert);
lookupBtn.addEventListener('click', handleLookup);

valueInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    handleLookup();
  }
});

setStatus('Waiting for input.');
