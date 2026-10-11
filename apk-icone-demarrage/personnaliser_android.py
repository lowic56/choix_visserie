#!/usr/bin/env python3
"""Personnalise l'APK avant compilation (lance par le workflow GitHub) :

  1. icone de l'application : vis cotee blanche sur fond bleu (couleur de l'interface)
  2. ecran de demarrage natif : fond uni (blanc / bleu nuit), sans logo Capacitor
  3. animation de demarrage : vis cotee animee, injectee dans www/index.html

Usage : python3 personnaliser_android.py [dossier_res_android] [www/index.html]
Necessite Pillow (pip install pillow). Aucune autre dependance.
"""
import os
import re
import sys

from PIL import Image, ImageDraw

RES = sys.argv[1] if len(sys.argv) > 1 else "android/app/src/main/res"
INDEX = sys.argv[2] if len(sys.argv) > 2 else "www/index.html"

BLEU = (37, 99, 235)            # #2563EB = couleur d'accent de l'interface
BLANC = (255, 255, 255, 255)
PAPIER_CLAIR, PAPIER_SOMBRE = "#FFFFFF", "#10151C"   # fond du schema (clair / sombre)

# --------------------------------------------------------------------------
# 1. ICONE
# --------------------------------------------------------------------------
M = 2048                      # image maitre ; l'unite de dessin vaut M/1024


def dessin_vis():
    """Vis cotee (vue de cote) en traits fins blancs, fond transparent, dans la zone sure.
    Cotes : longueur sous la vis + diametre a droite."""
    im = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = M / 1024.0
    sw = int(17 * u)                       # trait principal (fin)
    sf = int(11 * u)                       # traits secondaires et cotes
    x0 = 204 * u                           # bord gauche de la vis
    yc = (512 - 22) * u                    # axe de la vis
    xe = x0 + 540 * u                      # bout de la tige

    def ligne(pts, w):
        d.line(pts, fill=BLANC, width=w, joint="curve")
        for p in (pts[0], pts[-1]):        # bouts arrondis
            r = w / 2.0
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=BLANC)

    def fleche(x, y, sens, long_=36 * u, demi=15 * u):
        """Pointe de fleche pleine ; sens = 'g', 'd', 'h' ou 'b' (direction de la pointe)."""
        if sens == "g": pts = [(x, y), (x + long_, y - demi), (x + long_, y + demi)]
        elif sens == "d": pts = [(x, y), (x - long_, y - demi), (x - long_, y + demi)]
        elif sens == "h": pts = [(x, y), (x - demi, y + long_), (x + demi, y + long_)]
        else: pts = [(x, y), (x - demi, y - long_), (x + demi, y - long_)]
        d.polygon(pts, fill=BLANC)

    # tete hexagonale (vue de cote : 3 pans) + rondelle
    ligne([(x0, yc - 96 * u), (x0 + 108 * u, yc - 96 * u), (x0 + 108 * u, yc + 96 * u), (x0, yc + 96 * u), (x0, yc - 96 * u)], sw)
    ligne([(x0, yc - 32 * u), (x0 + 108 * u, yc - 32 * u)], sf)
    ligne([(x0, yc + 32 * u), (x0 + 108 * u, yc + 32 * u)], sf)
    ligne([(x0 + 108 * u, yc - 118 * u), (x0 + 134 * u, yc - 118 * u), (x0 + 134 * u, yc + 118 * u), (x0 + 108 * u, yc + 118 * u), (x0 + 108 * u, yc - 118 * u)], sw)
    # tige filetee avec chanfrein et filet
    ligne([(x0 + 134 * u, yc - 54 * u), (xe - 24 * u, yc - 54 * u), (xe, yc - 31 * u), (xe, yc + 31 * u),
           (xe - 24 * u, yc + 54 * u), (x0 + 134 * u, yc + 54 * u)], sw)
    ligne([(xe - 24 * u, yc - 54 * u), (xe - 24 * u, yc + 54 * u)], sf)
    for k in range(8):                     # filets
        xx = x0 + 168 * u + k * 44 * u
        if xx < xe - 40 * u:
            ligne([(xx, yc - 54 * u), (xx + 22 * u, yc + 54 * u)], int(sf * 0.7))
    # cote de longueur sous la vis
    yk = yc + 168 * u
    xa = x0 + 134 * u
    ligne([(xa, yc + 128 * u), (xa, yk + 22 * u)], int(sf * 0.8))
    ligne([(xe, yc + 66 * u), (xe, yk + 22 * u)], int(sf * 0.8))
    ligne([(xa + 30 * u, yk), (xe - 30 * u, yk)], sf)
    fleche(xa, yk, "g"); fleche(xe, yk, "d")
    # cote de diametre a droite de la tige
    xd = xe + 70 * u
    ligne([(xe + 14 * u, yc - 54 * u), (xd + 22 * u, yc - 54 * u)], int(sf * 0.8))
    ligne([(xe + 14 * u, yc + 54 * u), (xd + 22 * u, yc + 54 * u)], int(sf * 0.8))
    ligne([(xd, yc - 54 * u + 30 * u), (xd, yc + 54 * u - 30 * u)], sf)
    fleche(xd, yc - 54 * u, "h"); fleche(xd, yc + 54 * u, "b")
    return im


def echelle(im, k):
    """Redimensionne le dessin autour du centre (k < 1 : plus petit, k > 1 : plus grand)."""
    n = int(M * k)
    r = im.resize((n, n), Image.LANCZOS)
    out = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    out.paste(r, ((M - n) // 2, (M - n) // 2), r)
    return out


def ecrire(im, chemin, taille):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    im.resize((taille, taille), Image.LANCZOS).save(chemin, optimize=True)


def icones():
    art = dessin_vis()
    fg = echelle(art, 0.86)                 # adaptative : reste dans la zone sure (masque rond)
    fond = Image.new("RGBA", (M, M), BLEU + (255,))
    plein = Image.alpha_composite(fond, echelle(art, 1.22))   # icones classiques : dessin plus grand
    carre = Image.new("L", (M, M), 0)
    ImageDraw.Draw(carre).rounded_rectangle([0, 0, M - 1, M - 1], radius=int(M * 0.2), fill=255)
    rond = Image.new("L", (M, M), 0)
    ImageDraw.Draw(rond).ellipse([0, 0, M - 1, M - 1], fill=255)
    legacy = Image.new("RGBA", (M, M), (0, 0, 0, 0)); legacy.paste(plein, (0, 0), carre)
    legacy_r = Image.new("RGBA", (M, M), (0, 0, 0, 0)); legacy_r.paste(plein, (0, 0), rond)
    dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for k, px in dens.items():
        ecrire(legacy, f"{RES}/mipmap-{k}/ic_launcher.png", px)
        ecrire(legacy_r, f"{RES}/mipmap-{k}/ic_launcher_round.png", px)
        ecrire(fg, f"{RES}/mipmap-{k}/clv_foreground.png", int(px * 108 / 48))   # 108 dp
    ad = ('<?xml version="1.0" encoding="utf-8"?>\n'
          '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
          '    <background android:drawable="@color/clv_icon_bg"/>\n'
          '    <foreground android:drawable="@mipmap/clv_foreground"/>\n'
          '    <monochrome android:drawable="@mipmap/clv_foreground"/>\n'
          '</adaptive-icon>\n')
    os.makedirs(f"{RES}/mipmap-anydpi-v26", exist_ok=True)
    for nom in ("ic_launcher.xml", "ic_launcher_round.xml"):
        open(f"{RES}/mipmap-anydpi-v26/{nom}", "w", encoding="utf8").write(ad)


# --------------------------------------------------------------------------
# 2. ECRAN DE DEMARRAGE NATIF (fond uni, identique au fond de l'animation)
# --------------------------------------------------------------------------
def ecrire_xml(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    open(chemin, "w", encoding="utf8").write('<?xml version="1.0" encoding="utf-8"?>\n' + contenu)


def demarrage_natif():
    ecrire_xml(f"{RES}/values/clv_colors.xml",
               '<resources>\n'
               '    <color name="clv_icon_bg">#2563EB</color>\n'
               f'    <color name="clv_splash_bg">{PAPIER_CLAIR}</color>\n'
               '</resources>\n')
    ecrire_xml(f"{RES}/values-night/clv_colors.xml",
               f'<resources>\n    <color name="clv_splash_bg">{PAPIER_SOMBRE}</color>\n</resources>\n')
    ecrire_xml(f"{RES}/values/clv_bools.xml", '<resources>\n    <bool name="clv_barres_claires">true</bool>\n</resources>\n')
    ecrire_xml(f"{RES}/values-night/clv_bools.xml", '<resources>\n    <bool name="clv_barres_claires">false</bool>\n</resources>\n')
    os.makedirs(f"{RES}/drawable-nodpi", exist_ok=True)
    Image.new("RGBA", (288, 288), (0, 0, 0, 0)).save(f"{RES}/drawable-nodpi/clv_splash_vide.png")   # icone de demarrage invisible
    ecrire_xml(f"{RES}/values/styles.xml",
               '<resources>\n'
               '    <style name="AppTheme" parent="Theme.AppCompat.DayNight.DarkActionBar">\n'
               '        <item name="colorPrimary">#2563EB</item>\n'
               '        <item name="colorPrimaryDark">#1D4ED8</item>\n'
               '        <item name="colorAccent">#2563EB</item>\n'
               '    </style>\n'
               '    <style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight.NoActionBar">\n'
               '        <item name="windowActionBar">false</item>\n'
               '        <item name="windowNoTitle">true</item>\n'
               '        <item name="android:background">@color/clv_splash_bg</item>\n'
               '        <item name="android:statusBarColor">@color/clv_splash_bg</item>\n'
               '        <item name="android:windowLightStatusBar">@bool/clv_barres_claires</item>\n'
               '    </style>\n'
               '    <style name="AppTheme.NoActionBarLaunch" parent="Theme.SplashScreen">\n'
               '        <item name="android:background">@color/clv_splash_bg</item>\n'
               '        <item name="windowSplashScreenBackground">@color/clv_splash_bg</item>\n'
               '        <item name="windowSplashScreenAnimatedIcon">@drawable/clv_splash_vide</item>\n'
               '        <item name="postSplashScreenTheme">@style/AppTheme.NoActionBar</item>\n'
               '    </style>\n'
               '</resources>\n')


# --------------------------------------------------------------------------
# 3. ANIMATION DE DEMARRAGE (vis cotee) injectee dans la page
# --------------------------------------------------------------------------
SPLASH_CSS = """
#clv-splash{position:fixed;inset:0;z-index:1000;background:var(--paper,#fff);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
#clv-splash .sp-box{width:min(92vw,560px)}
#clv-splash svg{display:block;width:100%;height:auto;overflow:visible}
#clv-splash .sp-cv{fill:var(--paper,#fff)}
#clv-splash .sp-e{stroke:var(--acc,#2563eb);stroke-width:1.6}
#clv-splash .sp-c{stroke:var(--acc,#2563eb);stroke-width:2.4}
#clv-splash .sp-ar{fill:var(--acc,#2563eb)}
#clv-splash .sp-n{fill:var(--acc,#2563eb);font:800 38px system-ui,sans-serif}
#clv-splash .sp-t{margin-top:20px;font:800 24px system-ui,sans-serif;color:var(--tx,#14181f);opacity:0}
#clv-splash .sp-s{margin-top:4px;font:500 13.5px system-ui,sans-serif;color:var(--mut,#667085);opacity:0}
:root[data-eff=dark] #clv-splash image{filter:url(#inv)}
"""

SPLASH_JS = r"""
(function () {
  try {
    var q = location.search || "", force = /[?&]splash=1/.test(q);
    var app = !!window.Capacitor || (window.matchMedia && matchMedia("(display-mode: standalone)").matches);
    if (!force && !app) return;
    if (!force && window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var U = (typeof IMG_URL !== "undefined") ? IMG_URL : null;
    if (!U || !U.TH || !U.RDL || !U.ECROU) return;
    function im(n, x, y, w, h) {
      return '<image href="' + U[n] + '" x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" preserveAspectRatio="none"/>';
    }
    var el = document.createElement("div"); el.id = "clv-splash";
    el.innerHTML = '<div class="sp-box"><svg viewBox="60 395 640 295" xmlns="http://www.w3.org/2000/svg" role="img">' +
      '<defs><marker id="sp-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">' +
      '<path class="sp-ar" d="M0,1.5 L10,5 L0,8.5 z"/></marker></defs>' +
      '<g>' + im("TH", 112, 470, 557, 192) + im("RDL", 179, 470, 18, 192) + im("RDL", 356, 470, 18, 192) + im("ECROU", 373, 470, 88, 192) + '</g>' +
      '<rect id="sp-cv" class="sp-cv" x="60" y="395" width="640" height="295"/>' +
      '<g id="sp-g" opacity="0">' +
      '<line id="sp-ea" class="sp-e" x1="179" y1="417" x2="179" y2="417"/><line id="sp-eb" class="sp-e" x1="669" y1="417" x2="669" y2="417"/>' +
      '<line id="sp-l" class="sp-c" x1="179" y1="429" x2="179" y2="429" marker-start="url(#sp-ar)" marker-end="url(#sp-ar)"/></g>' +
      '<text id="sp-n" class="sp-n" x="424" y="414" text-anchor="middle" opacity="0">M6 \u00d7 0</text></svg></div>' +
      '<div class="sp-t" id="sp-t">Longueur de vis</div><div class="sp-s" id="sp-s">\u00c9crou \u00b7 Trou taraud\u00e9 \u00b7 Bridage</div>';
    var $ = function (id) { return el.querySelector("#" + id); };
    var cv = $("sp-cv"), g = $("sp-g"), ea = $("sp-ea"), eb = $("sp-eb"), ln = $("sp-l"), nn = $("sp-n"), tt = $("sp-t"), ss = $("sp-s");
    var cl = function (x) { return x < 0 ? 0 : x > 1 ? 1 : x; };
    var seg = function (t, a, b) { return cl((t - a) / (b - a)); };
    var eo = function (x) { return 1 - Math.pow(1 - x, 3); };
    var eio = function (x) { return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
    var t0 = null, fini = false;
    function fin() {
      if (fini) return; fini = true;
      el.style.transition = "opacity .25s"; el.style.opacity = "0";
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 300);
    }
    el.addEventListener("click", fin); el.addEventListener("touchstart", fin, { passive: true });
    function frame(ts) {
      if (fini) return;
      if (t0 === null) t0 = ts;
      var t = ts - t0;
      var r = eo(seg(t, 100, 750));                     // la vis apparait de gauche a droite
      cv.setAttribute("x", 60 + 640 * r); cv.setAttribute("width", 640 * (1 - r));
      var k = eio(seg(t, 700, 1250));                   // la cote se deploie
      g.setAttribute("opacity", k > 0 ? 1 : 0);
      ea.setAttribute("y2", 417 + 109 * k); eb.setAttribute("y2", 417 + 109 * k);
      ln.setAttribute("x2", 179 + 490 * k);
      var c = eo(seg(t, 1150, 1700));                   // la valeur s'incremente jusqu'a 35
      nn.textContent = "M6 \u00d7 " + Math.round(35 * c); nn.setAttribute("opacity", seg(t, 1150, 1350));
      tt.style.opacity = seg(t, 1000, 1500); ss.style.opacity = seg(t, 1200, 1700);
      if (t > 2200) { fin(); return; }
      requestAnimationFrame(frame);
    }
    document.body.appendChild(el);
    requestAnimationFrame(frame);
  } catch (e) { /* pas d'animation : l'application demarre normalement */ }
})();
"""

DEBUT, FIN = "<!--CLV-SPLASH-->", "<!--/CLV-SPLASH-->"


def injecter_animation():
    if not os.path.exists(INDEX):
        print("index.html introuvable :", INDEX); return
    s = open(INDEX, encoding="utf8").read()
    s = re.sub(re.escape(DEBUT) + r".*?" + re.escape(FIN), "", s, flags=re.S)   # idempotent
    bloc = DEBUT + "<style>" + SPLASH_CSS + "</style><script>" + SPLASH_JS + "</script>" + FIN
    i = s.rfind("</body>")
    s = (s[:i] + bloc + s[i:]) if i >= 0 else (s + bloc)
    open(INDEX, "w", encoding="utf8").write(s)
    print("animation de demarrage injectee dans", INDEX)


if __name__ == "__main__":
    for etape in (icones, demarrage_natif, injecter_animation):
        try:
            etape(); print("OK  :", etape.__name__)
        except Exception as e:                # une etape en echec ne bloque pas les autres
            print("ECHEC", etape.__name__, "->", e)
