# Générateur du mini site web du kit de planification (GitHub Pages).
# Lit contenu_fr.py (et contenu_en.py quand il existera) : même source que le Padlet.
# Usage : python3 build.py <dossier_source_contenu> <dossier_site>
import sys, os, re, html, json, importlib.util, unicodedata

SRC, OUT = sys.argv[1], sys.argv[2]

def load(lang):
    p = os.path.join(SRC, f"contenu_{lang}.py")
    if not os.path.exists(p):
        return None
    spec = importlib.util.spec_from_file_location(f"contenu_{lang}", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

# ------------------------------------------------------------------ textes d'interface
UI = {
 "fr": dict(
   html_lang="fr-CA", other="en", other_label="English",
   kicker="Mariages à l'Auberge des Gallant",
   home="Accueil", menu="Rubriques", sections="Les rubriques",
   on_page="Sur cette page", prev="Rubrique précédente", next="Rubrique suivante",
   back_top="Haut de page", print="Imprimer cette page",
   aub_step="Étape avec l'Auberge",
   check_note="Cochez les étapes au fur et à mesure : vos coches restent enregistrées sur cet appareil.",
   contact_t="Une question?", contact_name="Audrey Loiselle",
   contact_role="Coordonnatrice des ventes et événements mariage",
   phone="450-459-4241, poste 312", phone_href="+14504594241,312",
   email="mariage@gallant.qc.ca", contact_days="Présente du mardi au samedi",
   address="1171, chemin Saint-Henri, Sainte-Marthe (Québec) J0P 1W0",
   download="Télécharger", open_link="Ouvrir",
   all_t="Tout le kit, en un clic",
   all_kit=("Tout le kit en un seul téléchargement", "Kit_mariage_Auberge_des_Gallant.zip", "Guide, échéancier, budget, formulaire, plans de salle et marque-places, dans un fichier ZIP."),
   all_pdf=("Le kit complet en PDF", "Kit_de_planification_Auberge_des_Gallant.pdf", "Toutes les rubriques de ce site, à lire ou à imprimer."),
   title_suffix="Kit de planification · Auberge des Gallant",
   home_intro_t="Bienvenue dans votre kit",
   footer="Ce site est réservé aux mariés de l'Auberge des Gallant. Merci de ne pas le partager publiquement.",
   updated="Mis à jour le",
   search="Rechercher", search_ph="Un mot-clé : chambres, allergies, chandelles",
   search_none="Aucun résultat. Essayez un autre mot, ou écrivez-nous à mariage@gallant.qc.ca.",
   search_hint="Tapez un mot-clé pour trouver l'information dans toutes les rubriques.",
   close="Fermer",
 ),
 "en": dict(
   html_lang="en-CA", other="fr", other_label="Français",
   kicker="Weddings at Auberge des Gallant",
   home="Home", menu="Sections", sections="Sections",
   on_page="On this page", prev="Previous section", next="Next section",
   back_top="Back to top", print="Print this page",
   aub_step="Step with the Auberge",
   check_note="Tick off each step as you go: your checkmarks are saved on this device.",
   contact_t="Questions?", contact_name="Audrey Loiselle",
   contact_role="Wedding Sales and Events Coordinator",
   phone="450-459-4241, ext. 312", phone_href="+14504594241,312",
   email="mariage@gallant.qc.ca", contact_days="Available Tuesday to Saturday",
   address="1171 Chemin Saint-Henri, Sainte-Marthe, Quebec J0P 1W0",
   download="Download", open_link="Open",
   all_t="The whole kit, in one click",
   all_kit=("The whole kit in one download", "Wedding_kit_Auberge_des_Gallant.zip", "Guide, timeline, budget, form, floor plans and place cards, in one ZIP file."),
   all_pdf=("The complete kit as a PDF", "Planning_kit_Auberge_des_Gallant.pdf", "Every section of this site, to read or print."),
   title_suffix="Planning Kit · Auberge des Gallant",
   home_intro_t="Welcome to your kit",
   footer="This site is reserved for Auberge des Gallant couples. Please do not share it publicly.",
   updated="Updated on",
   search="Search", search_ph="A keyword: rooms, allergies, candles",
   search_none="No results. Try another word, or write to us at mariage@gallant.qc.ca.",
   search_hint="Type a keyword to find information across all sections.",
   close="Close",
 ),
}

# Ajustements propres au web (le texte source parle de « tableau » et de « colonnes » Padlet).
WEB_SUBST = {
 "fr": [
  ("Ce tableau réunit", "Ce site réunit"),
  ("Comment utiliser ce tableau", "Comment utiliser ce site"),
  ("Chaque colonne regroupe un sujet.", "Chaque rubrique regroupe un sujet."),
  ("**Colonnes thématiques**", "**Rubriques thématiques**"),
  ("tout au long de ce tableau", "tout au long de ce site"),
  (", juste ici, dans la section Hébergement.", ", plus bas sur cette page."),
  ("dans la colonne « Menu, bar et dégustation »", "dans la rubrique « Menu, bar et dégustation »"),
  ("notre tableau des fournisseurs", "notre page des fournisseurs"),
 ],
 "en": [
  ("This board brings together", "This site brings together"),
  ("How to use this board", "How to use this site"),
  ("Each column covers one topic.", "Each section covers one topic."),
  ("**Topic columns**", "**Topic sections**"),
  ("throughout this board", "throughout this site"),
  (", right here in the Accommodations section.", ", further down this page."),
  ('in the "Menu, bar and tasting" column', 'in the "Menu, bar and tasting" section'),
  ("our supplier board", "our supplier page"),
 ],
}

# Pièces jointes « @ » : texte source -> (libellé, cible). Cible = fichier dans downloads/<lang>/,
# URL complète, ou "#rubrique" (lien interne vers une rubrique, ancre facultative après /).
ATTACH = {
 "fr": {
  "Plan de votre salle (voir « Outils à télécharger »)": ("Plans de nos salles", "Plans_de_nos_salles.zip"),
  "Guide des marque-places (PDF)": ("Guide des marque-places (PDF)", "Guide_des_marque-places.pdf"),
  "Symboles en fichiers PNG (dans la trousse de gabarits)": ("Gabarits et symboles de marque-places (ZIP)", "Gabarits_de_marque-places.zip"),
  "padlet.com/mariageADG/liste-de-fournisseurs-recommandes-s0254d6m2cv4mz1d4cnq": ("Nos fournisseurs coups de cœur", "https://padlet.com/mariageADG/liste-de-fournisseurs-recommandes-s0254d6m2cv4mz1d4cnq"),
  "Echeancier_mariage_Auberge_des_Gallant.xlsx": ("Échéancier (Excel)", "Echeancier_mariage_Auberge_des_Gallant.xlsx"),
  "Budget_mariage_Auberge_des_Gallant.xlsx": ("Budget (Excel)", "Budget_mariage_Auberge_des_Gallant.xlsx"),
  "Trousse_plans_de_salle.zip": ("Plans de nos salles (ZIP)", "Plans_de_nos_salles.zip"),
  "Guide des marque-places FR.pdf": ("Guide des marque-places (PDF)", "Guide_des_marque-places.pdf"),
  "Trousse_marque-places_clients.zip": ("Gabarits de marque-places (ZIP)", "Gabarits_de_marque-places.zip"),
  "Formulaire_La_Grande_Finale.pdf": ("Formulaire « La Grande Finale » (PDF)", "Formulaire_La_Grande_Finale.pdf"),
  "Hébergement à proximité - Local lodging.pdf": ("Voir la fiche dans la rubrique Hébergement", "#hebergement/hebergement-et-transport-a-proximite"),
 },
 "en": {
  'Your hall\'s floor plan (see "Downloadable tools")': ("Floor plans of our reception halls", "Floor_plans_of_our_reception_halls.zip"),
  "Place card guide (PDF)": ("Place card guide (PDF)", "Place_card_guide.pdf"),
  "Symbols as PNG files (in the template kit)": ("Place card templates and symbols (ZIP)", "Place_card_templates.zip"),
  "padlet.com/mariageADG/liste-de-fournisseurs-recommandes-s0254d6m2cv4mz1d4cnq": ("Our favourite suppliers", "https://padlet.com/mariageADG/liste-de-fournisseurs-recommandes-s0254d6m2cv4mz1d4cnq"),
  "Wedding_timeline_Auberge_des_Gallant.xlsx": ("Planning timeline (Excel)", "Wedding_timeline_Auberge_des_Gallant.xlsx"),
  "Wedding_budget_Auberge_des_Gallant.xlsx": ("Wedding budget (Excel)", "Wedding_budget_Auberge_des_Gallant.xlsx"),
  "Floor_plan_kit.zip": ("Floor plans of our reception halls (ZIP)", "Floor_plans_of_our_reception_halls.zip"),
  "Place card guide EN.pdf": ("Place card guide (PDF)", "Place_card_guide.pdf"),
  "Place_card_kit.zip": ("Place card templates (ZIP)", "Place_card_templates.zip"),
  "La_Grande_Finale_form.pdf": ("\"La Grande Finale\" form (PDF)", "La_Grande_Finale_form.pdf"),
  "Hébergement à proximité - Local lodging.pdf": ("See the sheet in the Accommodations section", "#accommodations/nearby-lodging-and-transportation"),
 },
}

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s

esc = lambda s: html.escape(s, quote=True)

LANG_NOW = "fr"
def human_size(n):
    if LANG_NOW == "en":
        return f"{n/1024/1024:.1f} MB" if n >= 1024 * 1024 else f"{max(1, round(n/1024))} KB"
    if n >= 1024 * 1024: return f"{n/1024/1024:.1f} Mo".replace(".", ",")
    return f"{max(1, round(n/1024))} Ko"

ICON_DL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0-5-5m5 5 5-5M5 21h14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_EXT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6m0-6-9 9M18 14v6H4V6h6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_ARR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m0 0-6-6m6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def load_keywords(lang):
    p = os.path.join(SRC, f"padlet_{lang}.py")
    if not os.path.exists(p): return {}
    sys.path.insert(0, SRC)
    try:
        spec = importlib.util.spec_from_file_location(f"padlet_{lang}", p)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    except Exception as e:
        print("  ! mots-clés non chargés :", e); return {}
    finally:
        sys.path.pop(0)
    kw = {}
    for col in m.COLONNES:
        for pub in col[2]:
            if pub.get("mots"): kw[pub["titre"]] = pub["mots"]
    return kw

ICON_CAL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
ICON_SEARCH = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m15.5 15.5 5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'

class Lang:
    def __init__(self, code, mod):
        self.code, self.mod, self.ui = code, mod, UI[code]
        self.sections = mod.SECTIONS
        for s in self.sections:
            s["slug"] = slug(s["titre"])
            for p in s["posts"]:
                p["slug"] = slug(p["titre"])
        self.by_title = {s["titre"]: s for s in self.sections}
        self.used_subst = set()
        self.kw = load_keywords(code)

    def plain(self, line):
        m = re.match(r"^(##|-|\[\]|\[A\]|!|@|>|&|%)\s+(.*)$", line)
        k, t = (m.group(1), m.group(2)) if m else ("", line)
        if k in (">", "&", "%"): return ""
        if k == "@": t = ATTACH[self.code].get(t, (t, None))[0]
        return self.subst(t).replace("**", "")

    def index(self):
        out = []
        for s in self.sections:
            for p in s["posts"]:
                out.append({"s": s["titre"], "p": self.subst(p["titre"]), "u": f'{s["slug"]}.html#{p["slug"]}',
                            "k": self.kw.get(p["titre"], ""),
                            "t": " ".join(x for x in (self.plain(l) for l in p["corps"]) if x)})
        return out

    def subst(self, t):
        for i, (a, b) in enumerate(WEB_SUBST[self.code]):
            if a in t:
                t = t.replace(a, b); self.used_subst.add(i)
        return t

    def inline(self, t, depth):
        t = esc(self.subst(t))
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\b([\w.-]+@gallant\.qc\.ca)\b", r'<a href="mailto:\1">\1</a>', t)
        t = re.sub(r"(?<![/\w.])(www\.gallant\.ca)\b", r'<a href="https://\1" target="_blank" rel="noopener">\1</a>', t)
        t = re.sub(r"(?<![/\w.@])(aubergemontrigaud\.com)\b", r'<a href="https://\1" target="_blank" rel="noopener">\1</a>', t)
        def sec(m):
            name = html.unescape(m.group(1))
            s = self.by_title.get(name)
            if s:
                return f'« <a href="{s["slug"]}.html">{m.group(1)}</a> »'
            return m.group(0)
        t = re.sub(r"« ([^«»]+?) »", sec, t)
        def sec_en(m):
            s = self.by_title.get(html.unescape(m.group(1)))
            return f'"<a href="{s["slug"]}.html">{m.group(1)}</a>"' if s else m.group(0)
        t = re.sub(r"&quot;([^&]+?)&quot;", sec_en, t)
        return t

    def attachment(self, key):
        lab, tgt = ATTACH[self.code].get(key, (key, None))
        if tgt is None:
            print("  ! pièce jointe sans correspondance :", key)
            return f'<p>{esc(lab)}</p>'
        if tgt.startswith("http"):
            return f'<a class="file" href="{esc(tgt)}" target="_blank" rel="noopener"><span class="file-ic">{ICON_EXT}</span><span class="file-t">{esc(lab)}</span></a>'
        if tgt.startswith("#"):
            s, _, a = tgt[1:].partition("/")
            href = f"{s}.html" + (f"#{a}" if a else "")
            return f'<a class="file" href="{href}"><span class="file-ic">{ICON_ARR}</span><span class="file-t">{esc(lab)}</span></a>'
        path = os.path.join(OUT, "downloads", self.code, tgt)
        size = human_size(os.path.getsize(path)) if os.path.exists(path) else "?"
        if not os.path.exists(path): print("  ! fichier manquant :", path)
        ext = tgt.rsplit(".", 1)[-1].upper()
        return (f'<a class="file" href="../downloads/{self.code}/{esc(tgt)}" download><span class="file-ic">{ICON_DL}</span>'
                f'<span class="file-t">{esc(lab)}</span><span class="file-m">{ext} · {size}</span></a>')

    def body(self, sec, post):
        out, lst, chk = [], None, False
        page_id = f"{self.code}/{sec['slug']}/{post['slug']}"
        def close():
            nonlocal lst
            if lst: out.append(f"</{lst}>"); lst = None
        n = 0
        for line in post["corps"]:
            m = re.match(r"^(##|-|\[\]|\[A\]|!|@|>|&|%)\s+(.*)$", line)
            k, t = (m.group(1), m.group(2)) if m else ("", line)
            if k == "-":
                if lst != "ul": close(); out.append("<ul>"); lst = "ul"
                out.append(f"<li>{self.inline(t, 1)}</li>")
                continue
            if k in ("[]", "[A]"):
                if lst != "ul class=\"checks\"":
                    close(); out.append('<ul class="checks">'); lst = 'ul class="checks"'
                n += 1; chk = True
                cid = f"{page_id}/{n}"
                aub = k == "[A]"
                badge = f'<span class="aub" title="{esc(self.ui["aub_step"])}">◆<span class="sr"> {esc(self.ui["aub_step"])}</span></span>' if aub else ""
                out.append(f'<li{" class=\"is-aub\"" if aub else ""}><label><input type="checkbox" data-k="{esc(cid)}"><span class="box"></span><span class="ct">{badge}{self.inline(t, 1)}</span></label></li>')
                continue
            close()
            if lst is None and out and out[-1].startswith("</ul"): pass
            if k == "##": out.append(f"<h4>{self.inline(t, 1)}</h4>")
            elif k == "!": out.append(f'<p class="note">{self.inline(t, 1)}</p>')
            elif k == "@": out.append(self.attachment(t))
            elif k == ">": out.append(f'<figure class="float"><img src="../assets/img/{esc(t)}" alt="" loading="lazy"></figure>')
            elif k == "&": out.append(f'<figure class="logo-sm"><img src="../assets/img/{esc(t)}" alt="" loading="lazy"></figure>')
            elif k == "%": out.append(f'<figure class="wide"><img src="../assets/img/{esc(t)}" alt="" loading="lazy"></figure>')
            else: out.append(f"<p>{self.inline(t, 1)}</p>")
        close()
        return "\n".join(out), chk

# ------------------------------------------------------------------ dates clés pour l'agenda
# Décalage par rapport à la date du mariage : ("m", n) = n mois avant, ("d", n) = n jours (négatif = avant).
KEYDATES = [
 (("m", -12), "Planifier votre rencontre avec votre coordonnatrice mariage",
   "Entre 8 et 12 mois avant le mariage : menu, aménagement, hébergement et horaire de la réception. Écrivez-nous à mariage@gallant.qc.ca pour fixer le rendez-vous.",
   "Plan your meeting with your wedding coordinator",
   "Between 8 and 12 months before the wedding: menu, setup, accommodations and reception schedule. Write to mariage@gallant.qc.ca to set up the meeting."),
 (("m", -8), "Menu, bar et essai du menu mariage",
   "Entre 6 et 8 mois avant : planifiez le menu et le bar avec votre coordonnatrice, et réservez votre essai du menu mariage (sur rendez-vous, au moins 1 semaine d'avance).",
   "Menu, bar and wedding menu tasting",
   "Between 6 and 8 months before: plan the menu and bar with your coordinator, and book your wedding menu tasting (by appointment, at least 1 week ahead)."),
 (("m", -6), "Bloc de chambres : transmettre le lien à vos invités",
   "Le lien de réservation de votre bloc de chambres vous est envoyé dans les 6 mois précédant le mariage. Transmettez-le à vos invités dès que vous le recevez : seules les réservations faites par ce lien profitent du tarif préférentiel.",
   "Room block: share the link with your guests",
   "Your room block booking link is sent within the 6 months before the wedding. Share it with your guests as soon as you receive it: only bookings made through this link get the preferred rate."),
 (("m", -1), "Décompte final et formulaire « La Grande Finale »",
   "Envoyez votre décompte final des invités, vos choix de repas et le formulaire « La Grande Finale » à mariage@gallant.qc.ca. La rencontre finale a lieu dans les 30 jours qui précèdent le mariage; le paiement final s'y fait.",
   "Final count and \"La Grande Finale\" form",
   "Send your final guest count, meal choices and the \"La Grande Finale\" form to mariage@gallant.qc.ca. The final meeting takes place within 30 days of the wedding; the final payment is made at that meeting."),
 (("d", -28), "Plan de salle complet à remettre",
   "Remettez votre plan de salle complet lors de la rencontre finale : plan des tables, nombre de personnes et de chaque plat par table, invités avec allergies et numéros de table.",
   "Complete floor plan due",
   "Hand in your complete floor plan at the final meeting: table layout, number of guests and of each dish per table, guests with allergies and table numbers."),
 (("d", -21), "Marque-places et nourriture de l'extérieur",
   "Préparez vos marque-places selon notre guide. Dernier jour pour demander l'approbation de nourriture de l'extérieur à réchauffer (des frais s'appliquent).",
   "Place cards and outside food",
   "Prepare your place cards following our guide. Last day to request approval for outside food to be reheated (fees apply)."),
 (("d", -14), "Articles de décoration à apporter à l'Auberge",
   "Apportez nappes, chemins de table, serviettes, housses de chaises et tout ce qui est nécessaire au montage. À partir d'aujourd'hui, aucune modification au décompte final ni aux choix de repas.",
   "Bring your decor items to the Auberge",
   "Bring your tablecloths, table runners, napkins, chair covers and everything needed for the setup. From today, no changes to the final count or meal choices."),
 (("d", -3), "Plan de salle final",
   "72 heures avant, le plan de salle est considéré comme final. C'est aussi le premier jour pour déposer les cadeaux de vos invités en chambre, s'il y a lieu.",
   "Floor plan is final",
   "72 hours before, the floor plan is considered final. It is also the first day to drop off gifts for your guests' rooms, if any."),
 (("d", -1), "Cadeaux pour vos invités en chambre",
   "S'il y a lieu, remettez-nous les cadeaux prêts et emballés, idéalement aujourd'hui (au plus tard à 9 h 30 le jour du mariage).",
   "Gifts for your guests' rooms",
   "If any, bring us the gifts ready and wrapped, ideally today (no later than 9:30 a.m. on the wedding day)."),
 (("d", 0), "Notre mariage à l'Auberge des Gallant",
   "Accès à votre salle dès 8 h pour la décoration. Marque-places à installer sur les tables avant l'entrée des invités.",
   "Our wedding at Auberge des Gallant",
   "Access to your reception hall from 8 a.m. for decorating. Place cards to be set on the tables before guests come in."),
 (("d", 1), "Récupérer vos effets personnels",
   "Au plus tard à 7 h 30. Réglez aussi la facture ouverte du bar avant votre départ, s'il y a lieu.",
   "Pick up your belongings",
   "No later than 7:30 a.m. Also settle the open bar tab before you leave, if any."),
]
CAL_UI = {
 "fr": dict(t="Vos dates clés dans votre agenda", d="Inscrivez la date de votre mariage : nous calculons vos échéances avec l'Auberge. Ajoutez-les ensuite à votre agenda, avec un rappel une semaine avant et la veille.",
            lab="Date de votre mariage", ics="Tout ajouter à Outlook ou Apple", ics_n="Fichier agenda (.ics) avec rappels",
            g="Google", o="Outlook.com", past="Date passée", note="Sur Google Agenda, ajoutez chaque date avec le bouton Google : les rappels suivent vos réglages Google.",
            file="Dates_cles_mariage_Auberge_des_Gallant.ics", home="Ajoutez vos dates clés à votre agenda", wd="Le jour J"),
 "en": dict(t="Your key dates in your calendar", d="Enter your wedding date: we calculate your deadlines with the Auberge. Then add them to your calendar, with a reminder one week before and the day before.",
            lab="Your wedding date", ics="Add all to Outlook or Apple", ics_n="Calendar file (.ics) with reminders",
            g="Google", o="Outlook.com", past="Past date", note="On Google Calendar, add each date with the Google button: reminders follow your Google settings.",
            file="Key_wedding_dates_Auberge_des_Gallant.ics", home="Add your key dates to your calendar", wd="The wedding day"),
}

def cal_block(L):
    c = CAL_UI[L.code]; fr = L.code == "fr"
    data = [{"o": o, "t": (tf if fr else te), "d": (df if fr else de)} for o, tf, df, te, de in KEYDATES]
    return f"""<div class="cal" id="agenda">
  <p class="kicker">{esc(c['t'])}</p>
  <p class="cal-d">{esc(c['d'])}</p>
  <label class="cal-in"><span>{esc(c['lab'])}</span><input type="date" class="cal-date"></label>
  <div class="cal-out" hidden>
    <a class="cal-ics" href="#" download="{c['file']}"><span class="file-ic">{ICON_DL}</span><span><span class="big-t">{esc(c['ics'])}</span><span class="cal-n">{esc(c['ics_n'])}</span></span></a>
    <ol class="cal-list"></ol>
    <p class="cal-note">{esc(c['note'])}</p>
  </div>
  <script>window.ADG_CAL={json.dumps({"items": data, "ui": {"g": c["g"], "o": c["o"], "past": c["past"]}, "lang": L.ui["html_lang"]}, ensure_ascii=False)};</script>
</div>"""

# ------------------------------------------------------------------ gabarit
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+SC:wght@400;500&family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">')

def head(title, depth, lang_attr, desc=""):
    r = "../" * depth
    return f"""<!doctype html>
<html lang="{lang_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="googlebot" content="noindex, nofollow">
<meta name="referrer" content="same-origin">
<title>{esc(title)}</title>
<link rel="icon" href="{r}assets/img/favicon.png">
{FONTS}
<link rel="stylesheet" href="{r}assets/style.css?v={ASSET_V}">
</head>"""

def topbar(L, current=None):
    ui = L.ui
    items = "".join(
        f'<li><a href="{s["slug"]}.html"{" aria-current=\"page\"" if s is current else ""}><span class="n">{i:02d}</span>{esc(s["titre"])}</a></li>'
        for i, s in enumerate(L.sections, 1))
    other = ui["other"]
    other_href = f'../{other}/{current["slug_" + other] if current and ("slug_" + other) in current else "index"}.html' if other in LANGS else None
    sw = f'<a class="lang" href="{other_href}" lang="{other}">{ui["other_label"]}</a>' if other_href else ""
    return f"""<header class="top">
  <div class="top-in">
    <a class="brand" href="index.html" aria-label="{esc(ui['home'])}"><img src="../assets/img/logo.png" alt="Auberge des Gallant"></a>
    <nav class="top-nav">
      <div class="mini-search">
        <label class="mini-box"><span class="s-ic">{ICON_SEARCH}</span><span class="sr">{esc(ui['search'])}</span>
          <input type="search" class="search-q" placeholder="{esc(ui['search'])}" autocomplete="off" spellcheck="false" aria-controls="search"></label>
        <div class="search" id="search" hidden><ol class="search-res" aria-live="polite"></ol></div>
      </div>
      {sw}
      <button class="menu-btn" aria-expanded="false" aria-controls="menu"><span class="bars"></span><span class="m-l">{esc(ui['menu'])}</span></button>
    </nav>
  </div>
  <div class="menu" id="menu" hidden>
    <ol>{items}</ol>
  </div>
</header>"""

def contact(L):
    ui = L.ui
    return f"""<section class="contact">
  <p class="kicker">{esc(ui['contact_t'])}</p>
  <p class="c-name">{esc(ui['contact_name'])}</p>
  <p class="c-role">{esc(ui['contact_role'])}</p>
  <p class="c-lines"><a href="tel:{ui['phone_href']}">{esc(ui['phone'])}</a><span class="dot">·</span><a href="mailto:{ui['email']}">{ui['email']}</a></p>
  <p class="c-days">{esc(ui['contact_days'])}</p>
</section>"""

def footer(L):
    ui = L.ui
    return f"""<footer class="foot">
  <img src="../assets/img/favicon.png" alt="" class="foot-mark">
  <p>Auberge des Gallant · {esc(ui['address'])}</p>
  <p class="foot-note">{esc(ui['footer'])}</p>
</footer>
<script>window.ADG_UI={{none:{json.dumps(ui['search_none'])}}};</script>
<script src="../assets/search-{L.code}.js?v={ASSET_V}"></script>
<script src="../assets/app.js?v={ASSET_V}"></script>
</body></html>"""

def page_home(L):
    ui, m = L.ui, L.mod
    cards = "".join(f"""
    <a class="card" href="{s['slug']}.html">
      <span class="card-n">{i:02d}</span>
      <span class="card-t">{esc(s['titre'])}</span>
      <span class="card-d">{esc(s['intro'])}</span>
      <span class="card-go">{ICON_ARR}</span>
    </a>""" for i, s in enumerate(L.sections, 1))
    return f"""{head(f"{m.TITRE} · Auberge des Gallant", 1, ui['html_lang'])}
<body class="home">
{topbar(L)}
<main>
  <section class="hero-in">
    <p class="kicker">{esc(ui['kicker'])}</p>
    <h1>{esc(m.TITRE)}</h1>
    <p class="lede">{esc(m.SOUS_TITRE)}</p>
    <a class="home-cal" href="{L.sections[1]['slug']}.html#agenda"><span class="s-ic">{ICON_CAL}</span>{esc(CAL_UI[L.code]['home'])}<span class="hc-go">{ICON_ARR}</span></a>
  </section>
  <section class="grid-wrap">
    <h2 class="sc-title">{esc(ui['sections'])}</h2>
    <div class="grid">{cards}
    </div>
  </section>
  {contact(L)}
</main>
{footer(L)}"""

def page_section(L, i, s):
    ui = L.ui
    secs = L.sections
    toc = "".join(f'<li><a href="#{p["slug"]}">{esc(L.subst(p["titre"]))}</a></li>' for p in s["posts"])
    arts, any_chk = [], False
    for p in s["posts"]:
        b, chk = L.body(s, p); any_chk |= chk
        arts.append(f'<article class="post" id="{p["slug"]}"><h3>{esc(L.subst(p["titre"]))}</h3>\n{b}\n</article>')
    extra = cal_block(L) if i == 1 else ""
    if s is secs[-1]:   # Outils à télécharger : le kit complet en tête
        def big(t):
            lab, f, d = t
            path = os.path.join(OUT, "downloads", L.code, f)
            size = human_size(os.path.getsize(path)) if os.path.exists(path) else "?"
            ext = f.rsplit(".", 1)[-1].upper()
            return f'<a class="big-dl" href="../downloads/{L.code}/{f}" download><span class="file-ic">{ICON_DL}</span><span><span class="big-t">{esc(lab)}</span><span class="big-d">{esc(d)}</span><span class="file-m">{ext} · {size}</span></span></a>'
        extra = f'<div class="all"><p class="kicker">{esc(ui["all_t"])}</p><div class="all-in">{big(ui["all_kit"])}{big(ui["all_pdf"])}</div></div>'
    note = f'<p class="check-note">{esc(ui["check_note"])}</p>' if any_chk else ""
    prev = secs[i - 1] if i > 0 else None
    nxt = secs[i + 1] if i + 1 < len(secs) else None
    pn = '<nav class="pn">'
    pn += f'<a class="prev" href="{prev["slug"]}.html"><span class="pn-l">{esc(ui["prev"])}</span><span class="pn-t">{esc(prev["titre"])}</span></a>' if prev else '<span></span>'
    pn += f'<a class="next" href="{nxt["slug"]}.html"><span class="pn-l">{esc(ui["next"])}</span><span class="pn-t">{esc(nxt["titre"])}</span></a>' if nxt else '<a class="next" href="index.html"><span class="pn-l"></span><span class="pn-t">' + esc(ui["home"]) + '</span></a>'
    pn += '</nav>'
    return f"""{head(f"{s['titre']} · {ui['title_suffix']}", 1, ui['html_lang'])}
<body class="section">
{topbar(L, s)}
<main>
  <section class="sec-head">
    <p class="kicker"><a href="index.html">{esc(ui['home'])}</a><span class="dot">·</span>{i+1:02d}</p>
    <h1>{esc(s['titre'])}</h1>
    <p class="lede">{esc(s['intro'])}</p>
    <span class="rule"></span>
  </section>
  <div class="sec-body">
    <aside class="toc"><p class="toc-t">{esc(ui['on_page'])}</p><ol>{toc}</ol>
      <button class="print" onclick="window.print()">{esc(ui['print'])}</button></aside>
    <div class="posts">{extra}{note}
{chr(10).join(arts)}
    </div>
  </div>
  {pn}
  {contact(L)}
</main>
{footer(L)}"""

def page_landing():
    btns = []
    for code, lab, sub in (("fr", "Français", "Votre kit de planification"), ("en", "English", "Your planning kit")):
        if code in LANGS:
            btns.append(f'<a class="choose" href="{code}/index.html" lang="{code}"><span class="ch-l">{lab}</span><span class="ch-s">{sub}</span></a>')
        else:
            btns.append(f'<span class="choose soon" lang="{code}"><span class="ch-l">{lab}</span><span class="ch-s">Coming soon</span></span>')
    return f"""{head("Kit de planification · Planning Kit · Auberge des Gallant", 0, "fr-CA")}
<body class="landing">
<main class="land">
  <div class="land-bg" role="img" aria-label=""></div>
  <div class="land-in">
    <img class="land-logo" src="assets/img/logo-blanc.png" alt="Auberge des Gallant">
    <p class="land-k">Mariages · Weddings</p>
    <h1><span lang="fr">Votre kit de planification</span><span class="sep"></span><span lang="en">Your planning kit</span></h1>
    <div class="choices">{''.join(btns)}</div>
  </div>
</main>
</body></html>"""

# ------------------------------------------------------------------ construction
import hashlib
_h = hashlib.sha1()
for _f in ("style.css", "app.js"):
    _h.update(open(os.path.join(OUT, "assets", _f), "rb").read())
for _c in ("fr", "en"):
    _p = os.path.join(SRC, f"contenu_{_c}.py")
    if os.path.exists(_p): _h.update(open(_p, "rb").read())
ASSET_V = _h.hexdigest()[:8]
LANGS = {}
for code in ("fr", "en"):
    mod = load(code)
    if mod: LANGS[code] = Lang(code, mod)
# Correspondance des rubriques entre langues (même ordre) pour le bouton de langue.
if "fr" in LANGS and "en" in LANGS:
    for a, b in zip(LANGS["fr"].sections, LANGS["en"].sections):
        a["slug_en"] = b["slug"]; b["slug_fr"] = a["slug"]

def write(rel, txt):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(txt)

write("index.html", page_landing())
for code, L in LANGS.items():
    LANG_NOW = code
    write(f"{code}/index.html", page_home(L))
    for i, s in enumerate(L.sections):
        write(f"{code}/{s['slug']}.html", page_section(L, i, s))
    write(f"assets/search-{code}.js", "window.ADG_IDX=" + json.dumps(L.index(), ensure_ascii=False, separators=(",", ":")) + ";\n")
    unused = [WEB_SUBST[code][i][0] for i in range(len(WEB_SUBST[code])) if i not in L.used_subst]
    if unused: print(f"  ! [{code}] ajustements web non utilisés :", unused)
    print(f"{code} : {len(L.sections)} rubriques, {sum(len(s['posts']) for s in L.sections)} publications")
write("robots.txt", "User-agent: *\nDisallow: /\n")
write(".nojekyll", "")
