function resizeIframe() {
    var iframe = document.getElementById('childIframe');
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    iframe.style.width = iframe.contentWindow.document.body.scrollWidth + 'px';
}
