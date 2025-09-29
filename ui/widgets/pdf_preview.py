from __future__ import annotations
import io
from typing import Optional

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock

class PdfPreview(BoxLayout):
    """Einfache PDF-Vorschau (1 Seite sichtbar) mit Fit-to-Width, Zoom & Seitenwechsel.
       Render-Engine: pypdfium2 (empfohlen), Fallback: PyMuPDF (pymupdf)."""

    source = StringProperty("")        # Pfad zur PDF
    page_index = NumericProperty(0)    # 0-basiert
    page_count = NumericProperty(0)
    fit_to_width = BooleanProperty(True)
    zoom = NumericProperty(1.0)

    _doc = ObjectProperty(None, allownone=True)
    _engine = StringProperty("")       # "pdfium" | "pymupdf" | ""
    _img = ObjectProperty(None, allownone=True)
    _sv = ObjectProperty(None, allownone=True)
    _toolbar = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(6), **kwargs)

        # Toolbar
        tb = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        self._btn_prev = Button(text="◀", size_hint=(None, None), size=(dp(36), dp(32)))
        self._btn_next = Button(text="▶", size_hint=(None, None), size=(dp(36), dp(32)))
        self._lbl_page = Label(text="Seite 0/0", size_hint=(None, None), size=(dp(110), dp(32)), halign="center", valign="middle")
        self._lbl_page.bind(size=lambda i, v: setattr(i, "text_size", v))
        self._btn_zoom_out = Button(text="–", size_hint=(None, None), size=(dp(36), dp(32)))
        self._btn_zoom_in  = Button(text="+", size_hint=(None, None), size=(dp(36), dp(32)))
        self._btn_fit = Button(text="Breite", size_hint=(None, None), size=(dp(64), dp(32)))

        self._btn_prev.bind(on_release=lambda *_: self.prev_page())
        self._btn_next.bind(on_release=lambda *_: self.next_page())
        self._btn_zoom_out.bind(on_release=lambda *_: self.set_zoom(max(0.25, self.zoom - 0.1)))
        self._btn_zoom_in.bind(on_release=lambda *_: self.set_zoom(min(5.0, self.zoom + 0.1)))
        self._btn_fit.bind(on_release=lambda *_: self.toggle_fit())

        tb.add_widget(self._btn_prev)
        tb.add_widget(self._btn_next)
        tb.add_widget(self._lbl_page)
        tb.add_widget(self._btn_zoom_out)
        tb.add_widget(self._btn_zoom_in)
        tb.add_widget(self._btn_fit)
        self._toolbar = tb
        self.add_widget(tb)

        # Scroll + Image
        sv = ScrollView(do_scroll_x=True, do_scroll_y=True, bar_width=dp(6))
        img = Image(allow_stretch=True, keep_ratio=True, size_hint=(None, None))
        sv.add_widget(img)
        self._sv = sv
        self._img = img
        self.add_widget(sv)

        # Re-render bei Größenänderung throtteln
        self._resize_ev = None
        self.bind(size=self._schedule_resize)

        # Initial versuchen zu öffnen (falls source bereits gesetzt)
        Clock.schedule_once(lambda dt: self._open_if_needed(), 0)

    # ---------- Public Controls ----------
    def toggle_fit(self):
        self.fit_to_width = not self.fit_to_width
        self._render_current()

    def set_zoom(self, z: float):
        self.zoom = float(z)
        self._render_current()

    def next_page(self):
        if self.page_index+1 < self.page_count:
            self.page_index += 1
            self._render_current()

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self._render_current()

    # ---------- Lifecycle ----------
    def on_source(self, *_):
        # Guard: interne Widgets schon da?
        if not self._img or not self._sv:
            Clock.schedule_once(lambda dt: self._open_if_needed(), 0)
            return
        self._open_if_needed()

    def on_fit_to_width(self, *_):
        self._render_current()

    def on_zoom(self, *_):
        if not self.fit_to_width:
            self._render_current()

    def _schedule_resize(self, *_):
        if self._resize_ev:
            self._resize_ev.cancel()
        self._resize_ev = Clock.schedule_once(lambda dt: self._render_current(), 0.05)

    # ---------- Open / Close ----------
    def _open_if_needed(self):
        if not self.source:
            return
        # Erst pdfium probieren
        self._close_doc()
        try:
            import pypdfium2 as pdfium  # noqa
            self._engine = "pdfium"
        except Exception:
            try:
                import fitz  # PyMuPDF  # noqa
                self._engine = "pymupdf"
            except Exception:
                self._engine = ""
        if not self._engine:
            self._lbl_page.text = "Kein PDF-Renderer installiert (pypdfium2/pymupdf)."
            return

        try:
            if self._engine == "pdfium":
                import pypdfium2 as pdfium
                self._doc = pdfium.PdfDocument(self.source)
                self.page_count = len(self._doc)
            else:
                import fitz
                self._doc = fitz.open(self.source)
                self.page_count = self._doc.page_count
            self.page_index = 0
            self._render_current()
        except Exception as e:
            self._lbl_page.text = f"PDF konnte nicht geöffnet werden: {e}"

    def _close_doc(self):
        try:
            if self._engine == "pymupdf" and self._doc:
                self._doc.close()
        except Exception:
            pass
        self._doc = None

    # ---------- Rendering ----------
    def _render_current(self):
        if not self._doc or self.page_count == 0 or not self._sv or not self._img:
            return
        w_avail = max(1.0, float(self._sv.width) - dp(12))
        try:
            if self._engine == "pdfium":
                img = self._render_with_pdfium(w_avail)
            else:
                img = self._render_with_pymupdf(w_avail)
            # PIL -> Texture
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            ci = CoreImage(buf, ext="png")
            tex = ci.texture
            self._img.texture = tex

            # Größe des Image-Widgets passend setzen
            iw, ih = tex.size
            if self.fit_to_width:
                draw_w = w_avail
                scale = draw_w / max(1.0, float(iw))
                draw_h = ih * scale
                self._img.size = (draw_w, draw_h)
            else:
                self._img.size = (iw * self.zoom, ih * self.zoom)

            self._lbl_page.text = f"Seite {self.page_index+1}/{self.page_count}"
        except Exception as e:
            self._lbl_page.text = f"Render-Fehler: {e}"

    def _render_with_pdfium(self, w_avail: float):
        import pypdfium2 as pdfium
        page = self._doc[self.page_index]
        pw, ph = page.get_size()  # Punkte (1/72 inch)
        base_scale = w_avail / max(1.0, float(pw)) if self.fit_to_width else self.zoom
        bmp = page.render(scale=base_scale)  # PdfBitmap
        return bmp.to_pil()

    def _render_with_pymupdf(self, w_avail: float):
        import fitz  # PyMuPDF
        page = self._doc.load_page(self.page_index)
        rect = page.rect
        if self.fit_to_width:
            sx = w_avail / max(1.0, float(rect.width))
        else:
            sx = self.zoom
        mat = fitz.Matrix(sx, sx)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        from PIL import Image as PILImage
        mode = "RGB"
        img = PILImage.frombytes(mode, [pix.width, pix.height], pix.samples)
        return img

    # ---------- Cleanup ----------
    def on_parent(self, *_):
        if self.parent is None:
            self._close_doc()
