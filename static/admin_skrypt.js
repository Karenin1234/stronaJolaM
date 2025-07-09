document.addEventListener('DOMContentLoaded', () => {
  // --- Elementy DOM ---
  // Nawigacja
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const toStep2Btn = document.getElementById('toStep2');
  const backBtn = document.getElementById('backToStep1');

  // Informacje o poście
  const titleInput = document.getElementById('blogTitle');
  const descInput = document.getElementById('blogDesc');

  // Okładka
  const coverInput = document.getElementById('coverUpload');
  const coverPreview = document.getElementById('coverPreview');

  // Edytor
  const blogContent = document.getElementById('blogContent');
  const mediaInput = document.getElementById('mediaUpload');
  const insertImageBtn = document.getElementById('insertImageHereBtn');
  const insertVideoBtn = document.getElementById('insertVideoHereBtn');

  // Przyciski formatowania
  const boldBtn = document.getElementById('boldBtn');
  const italicBtn = document.getElementById('italicBtn');
  const underlineBtn = document.getElementById('underlineBtn');
  const strikeBtn = document.getElementById('strikeBtn');
  const alignLeftBtn = document.getElementById('alignLeft');
  const alignCenterBtn = document.getElementById('alignCenter');
  const alignRightBtn = document.getElementById('alignRight');
  const fontFamilySel = document.getElementById('fontFamily');
  const fontSizeSel = document.getElementById('fontSize');
  const textColorSel = document.getElementById('textColor');
  const dividerBtn = document.getElementById('insertDividerBtn');
  const dividerThickness = document.getElementById('dividerThickness');
  const lineHeightSel = document.getElementById('lineHeight');

  // Publikacja
  const publishBtn = document.getElementById('publishBtn');
  const saveDraftBtn = document.getElementById('saveDraftBtn');

  // Sidebar
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');

  // --- Walidacja kroku 1 ---
  function validateStep1() {
    if (titleInput && descInput && toStep2Btn) {
      toStep2Btn.disabled = !(titleInput.value.trim() && descInput.value.trim());
    }
  }

  if (titleInput) titleInput.addEventListener('input', validateStep1);
  if (descInput) descInput.addEventListener('input', validateStep1);

  // --- Podgląd okładki ---
  if (coverInput && coverPreview) {
    const coverFileName = document.getElementById('coverFileName');

    coverInput.addEventListener('change', function() {
      const file = this.files[0];
      if (!file) {
        coverPreview.innerHTML = '';
        if (coverFileName) coverFileName.textContent = 'Nie wybrano pliku';
        return;
      }

      // Walidacja rozmiaru pliku
      if (file.size > 5 * 1024 * 1024) {
        alert('Plik okładki jest zbyt duży (max 5MB)');
        this.value = '';
        if (coverFileName) coverFileName.textContent = 'Nie wybrano pliku';
        return;
      }

      if (coverFileName) coverFileName.textContent = file.name;

      const reader = new FileReader();
      reader.onload = e => {
        coverPreview.innerHTML = `
          <img src="${e.target.result}"
               class="rounded-md border border-gray-600 max-h-40"
               alt="Podgląd okładki">
        `;
      };
      reader.readAsDataURL(file);
    });
  }

  // --- Nawigacja między krokami ---
  if (toStep2Btn && step1 && step2) {
    toStep2Btn.addEventListener('click', () => {
      step1.classList.add('hidden');
      step2.classList.remove('hidden');
      if (blogContent) blogContent.focus();
    });
  }

  if (backBtn && step1 && step2) {
    backBtn.addEventListener('click', () => {
      step2.classList.add('hidden');
      step1.classList.remove('hidden');
    });
  }

  // Inicjalna walidacja
  validateStep1();

  // --- Sidebar ---
  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      const isOpen = sidebar.classList.contains('open');
      sidebarToggle.innerHTML = isOpen
        ? '<i class="fas fa-chevron-right"></i>'
        : '<i class="fas fa-chevron-left"></i>';
      sidebar.style.transform = isOpen ? 'translateX(0)' : 'translateX(100%)';
    });
  }

  // --- Funkcje edytora ---
  function execCmd(cmd, value = null) {
    document.execCommand(cmd, false, value);
    if (blogContent) blogContent.focus();
  }

  // Przyciski formatowania tekstu
  const formatButtons = [
    { btn: boldBtn, cmd: 'bold' },
    { btn: italicBtn, cmd: 'italic' },
    { btn: underlineBtn, cmd: 'underline' },
    { btn: strikeBtn, cmd: 'strikeThrough' },
    { btn: alignLeftBtn, cmd: 'justifyLeft' },
    { btn: alignCenterBtn, cmd: 'justifyCenter' },
    { btn: alignRightBtn, cmd: 'justifyRight' }
  ];

  formatButtons.forEach(({btn, cmd}) => {
    if (btn) btn.addEventListener('click', () => execCmd(cmd));
  });

  // Listy rozwijane
  const formatSelects = [
    { select: fontFamilySel, cmd: 'fontName' },
    { select: fontSizeSel, cmd: 'fontSize' },
    { select: textColorSel, cmd: 'foreColor' }
  ];

  formatSelects.forEach(({select, cmd}) => {
    if (select) select.addEventListener('change', () => execCmd(cmd, select.value));
  });

  // Divider
  if (dividerBtn && dividerThickness) {
    dividerBtn.addEventListener('click', () => {
      execCmd('insertHTML', `
        <hr class="custom-divider"
            style="border-top:${dividerThickness.value}px dashed #f59e0b;">
      `);
    });
  }

  // Wysokość linii
  if (lineHeightSel && blogContent) {
    lineHeightSel.addEventListener('change', () => {
      blogContent.style.lineHeight = lineHeightSel.value;
    });
  }

  // --- Wstawianie mediów ---
  if (mediaInput && insertImageBtn && insertVideoBtn && blogContent) {
    let mediaType = null;

    insertImageBtn.addEventListener('click', () => {
      mediaType = 'image';
      mediaInput.click();
    });

    insertVideoBtn.addEventListener('click', () => {
      mediaType = 'video';
      mediaInput.click();
    });

    mediaInput.addEventListener('change', function() {
      const file = this.files[0];
      if (!file) return;

      // Walidacja rozmiaru pliku
      if (file.size > 10 * 1024 * 1024) {
        alert(`Plik ${file.name} jest zbyt duży (max 10MB)`);
        this.value = '';
        return;
      }

      const reader = new FileReader();
      reader.onload = e => {
        const mediaElement = mediaType === 'image'
          ? `<img src="${e.target.result}"
                   class="rounded-md mb-4"
                   alt="Wstawiony obraz">`
          : `<video src="${e.target.result}"
                   controls
                   class="rounded-md mb-4"></video>`;

        // Wstaw w aktualnej pozycji kursora
        const selection = window.getSelection();
        if (!selection.rangeCount) return;

        const range = selection.getRangeAt(0);
        range.deleteContents();

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = mediaElement;
        const fragment = document.createDocumentFragment();

        while (tempDiv.firstChild) {
          fragment.appendChild(tempDiv.firstChild);
        }

        range.insertNode(fragment);

        // Poprawka dla błędu Range.setStartAfter
        if (fragment.lastChild) {
          range.setStartAfter(fragment.lastChild);
          range.collapse(true);
          selection.removeAllRanges();
          selection.addRange(range);
        } else {
          // Alternatywa jeśli nie ma lastChild
          range.collapse(false);
        }

        // Wyczyść input
        this.value = '';
        mediaType = null;
      };
      reader.readAsDataURL(file);
    });
  }

  // --- Zapis wersji roboczej ---
  if (saveDraftBtn) {
    saveDraftBtn.addEventListener('click', () => {
      alert('Wersja robocza zapisana!');
      // Logika zapisu do localStorage
    });
  }

  // --- Publikacja posta ---
  if (publishBtn && titleInput && descInput && blogContent) {
    publishBtn.addEventListener('click', async () => {
      // Walidacja
      if (!titleInput.value.trim() || !descInput.value.trim() || !blogContent.innerText.trim()) {
        alert('Proszę uzupełnić tytuł, opis i treść posta!');
        return;
      }

      // Przygotowanie danych
      const postData = {
        title: titleInput.value.trim(),
        description: descInput.value.trim(),
        timestamp: new Date().toISOString(),
        html: blogContent.innerHTML,
        media: []
      };

      // Znajdź wszystkie media w treści
      const parser = new DOMParser();
      const doc = parser.parseFromString(postData.html, 'text/html');
      const mediaElements = doc.querySelectorAll('img[src^="data:"], video[src^="data:"]');

      const formData = new FormData();
      let mediaIndex = 0;

      // Przetwarzanie mediów
      for (const element of mediaElements) {
        const src = element.getAttribute('src');
        const match = src.match(/^data:(.+?);base64,(.+)$/);

        if (match) {
          const mimeType = match[1];
          const base64Data = match[2];
          const extension = mimeType.split('/')[1];
          const mediaId = `media_${Date.now()}_${mediaIndex}.${extension}`;

          // Konwersja Base64 na Blob (optymalizowana)
          const byteCharacters = atob(base64Data);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: mimeType });

          formData.append('media', blob, mediaId);

          // Zastąp src w HTML
          element.setAttribute('src', `media://${mediaId}`);

          // Zapisz informacje o mediach
          postData.media.push({
            id: mediaId,
            type: element.tagName.toLowerCase(),
            position: mediaIndex
          });

          mediaIndex++;
        }
      }

      // Aktualizuj HTML po zmianach
      postData.html = doc.documentElement.innerHTML;

      // Dodaj okładkę jeśli istnieje
      if (coverInput && coverInput.files[0]) {
        formData.append('cover', coverInput.files[0]);
        postData.cover_image = coverInput.files[0].name;
      }

      // Dodaj dane JSON
      formData.append('json', new Blob(
        [JSON.stringify(postData)],
        { type: 'application/json' }
      ));

      // Wyślij do serwera
      try {
        const response = await fetch('http://localhost:8127/api/upload-post', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          let errorMsg = 'Błąd serwera';
          try {
            const errorData = await response.json();
            errorMsg = errorData.error || errorData.message || errorMsg;
          } catch (e) {
            errorMsg = await response.text();
          }
          throw new Error(errorMsg);
        }

        const result = await response.json();
        alert(`Post został opublikowany! ID: ${result.post_id}`);

        // Reset formularza
        titleInput.value = '';
        descInput.value = '';
        blogContent.innerHTML = '';
        if (coverPreview) coverPreview.innerHTML = '';
        if (coverInput) coverInput.value = '';
        const coverFileName = document.getElementById('coverFileName');
        if (coverFileName) coverFileName.textContent = 'Nie wybrano pliku';

        step2.classList.add('hidden');
        step1.classList.remove('hidden');
        validateStep1();

      } catch (error) {
        console.error('Błąd publikacji:', error);
        alert(`Wystąpił błąd: ${error.message}`);
      }
    });
  }
});