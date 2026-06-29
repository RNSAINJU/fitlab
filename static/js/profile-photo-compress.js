(function () {
  var MAX_EDGE = 1200;
  var JPEG_QUALITY = 0.82;
  var MAX_BYTES = 5 * 1024 * 1024;

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function setHint(el, message, isError) {
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("profile-hint--error", !!isError);
    el.classList.toggle("profile-hint--ok", !isError && message.indexOf("Compressed") !== -1);
  }

  function setPreview(preview, src, initial) {
    if (!preview) return;
    preview.innerHTML = "";
    if (src) {
      var img = document.createElement("img");
      img.src = src;
      img.alt = "Profile photo preview";
      img.className = "profile-photo-preview__img";
      preview.appendChild(img);
    } else if (initial) {
      var span = document.createElement("span");
      span.className = "profile-photo-preview__initial";
      span.textContent = initial;
      preview.appendChild(span);
    }
  }

  function replaceInputFile(input, file) {
    var transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
  }

  function loadImageFromFile(file) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("Could not read image."));
      };
      img.src = url;
    });
  }

  function canvasToBlob(canvas, type, quality) {
    return new Promise(function (resolve, reject) {
      canvas.toBlob(
        function (blob) {
          if (blob) resolve(blob);
          else reject(new Error("Compression failed."));
        },
        type,
        quality
      );
    });
  }

  async function compressImage(file) {
    var image = await loadImageFromFile(file);
    var width = image.naturalWidth || image.width;
    var height = image.naturalHeight || image.height;
    var scale = Math.min(MAX_EDGE / width, MAX_EDGE / height, 1);
    var targetW = Math.max(1, Math.round(width * scale));
    var targetH = Math.max(1, Math.round(height * scale));

    var canvas = document.createElement("canvas");
    canvas.width = targetW;
    canvas.height = targetH;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0, targetW, targetH);

    var quality = JPEG_QUALITY;
    var blob = await canvasToBlob(canvas, "image/jpeg", quality);

    while (blob.size > MAX_BYTES && quality > 0.45) {
      quality -= 0.08;
      blob = await canvasToBlob(canvas, "image/jpeg", quality);
    }

    if (blob.size > MAX_BYTES) {
      throw new Error("Photo is still too large after compression. Try a smaller image.");
    }

    var baseName = (file.name || "profile").replace(/\.[^.]+$/, "");
    return new File([blob], baseName + ".jpg", {
      type: "image/jpeg",
      lastModified: Date.now(),
    });
  }

  function init() {
    var form = document.querySelector(".profile-form");
    var input = document.getElementById("id_profile_photo");
    var preview = document.getElementById("profile-photo-preview");
    var hint = document.getElementById("profile-photo-hint");
    var submitBtn = form ? form.querySelector('button[type="submit"]') : null;
    var initial = preview ? preview.getAttribute("data-initial") || "" : "";
    var originalSrc = preview ? preview.getAttribute("data-original-src") || "" : "";

    if (!form || !input) return;

    var compressTask = null;
    var skipCompressOnSubmit = false;

    function setBusy(busy) {
      input.disabled = busy;
      if (submitBtn) {
        submitBtn.disabled = busy;
        submitBtn.textContent = busy ? "Compressing photo…" : "Save profile";
      }
    }

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      var removeCheckbox = document.getElementById("id_remove_profile_photo");
      if (!file) {
        compressTask = null;
        setPreview(preview, originalSrc || null, originalSrc ? "" : initial);
        setHint(hint, "JPG, PNG, or WebP. Compressed automatically before upload.");
        return;
      }

      if (!file.type || file.type.indexOf("image/") !== 0) {
        input.value = "";
        setHint(hint, "Please choose a JPG, PNG, or WebP image.", true);
        return;
      }

      if (removeCheckbox) removeCheckbox.checked = false;

      compressTask = (async function () {
        setBusy(true);
        setHint(hint, "Compressing photo before upload…");
        try {
          var compressed = await compressImage(file);
          replaceInputFile(input, compressed);
          setPreview(preview, URL.createObjectURL(compressed), "");
          setHint(
            hint,
            "Compressed " +
              formatSize(file.size) +
              " → " +
              formatSize(compressed.size) +
              " before upload."
          );
        } catch (err) {
          input.value = "";
          setPreview(preview, originalSrc || null, originalSrc ? "" : initial);
          setHint(hint, err.message || "Could not compress photo.", true);
          throw err;
        } finally {
          setBusy(false);
        }
      })();
    });

    form.addEventListener("submit", function (event) {
      if (skipCompressOnSubmit) return;
      if (!compressTask) return;

      event.preventDefault();
      compressTask
        .then(function () {
          skipCompressOnSubmit = true;
          form.requestSubmit();
        })
        .catch(function () {
          /* Errors already shown on the hint. */
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
