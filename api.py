from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

df = pd.read_csv('dataset_final_propre.csv', encoding='utf-8')
df['mois'] = pd.to_datetime(df['mois'], errors='coerce')

@app.route('/')
def index():
    return jsonify({
        "message": "API Offres d'emploi au Sénégal",
        "endpoints": [
            "/api/offres",
            "/api/secteurs",
            "/api/villes",
            "/api/contrats",
            "/api/competences",
            "/api/evolution"
        ]
    })

@app.route('/api/offres')
def offres():
    secteur = request.args.get('secteur')
    ville = request.args.get('ville')
    annee = request.args.get('annee')
    contrat = request.args.get('contrat')
    
    data = df.copy()
    if secteur:
        data = data[data['secteur'] == secteur]
    if ville:
        data = data[data['ville'] == ville]
    if annee:
        data = data[data['mois'].dt.year == int(annee)]
    if contrat:
        data = data[data['contrat'] == contrat]
    
    return jsonify({
        "total": len(data),
        "offres": data[['intitule_poste', 'entreprise', 'ville', 'secteur', 'contrat', 'mois']].fillna('').to_dict('records')
    })

@app.route('/api/secteurs')
def secteurs():
    result = df['secteur'].value_counts().dropna()
    result = result[~result.index.str.contains('Non', na=False)]
    return jsonify({
        "total_secteurs": len(result),
        "secteurs": [{"secteur": k, "nb_offres": int(v)} for k, v in result.items()]
    })

@app.route('/api/villes')
def villes():
    result = df['ville'].value_counts().dropna()
    result = result[~result.index.str.contains('Non', na=False)]
    result = result[result.index != 'zone rurale']
    return jsonify({
        "total_villes": len(result),
        "villes": [{"ville": k, "nb_offres": int(v)} for k, v in result.items()]
    })

@app.route('/api/contrats')
def contrats():
    result = df['contrat'].value_counts().dropna()
    result = result[~result.index.str.contains('Non', na=False)]
    return jsonify({
        "contrats": [{"contrat": k, "nb_offres": int(v)} for k, v in result.items()]
    })

@app.route('/api/competences')
def competences():
    a_exclure = ['Non spécifié', 'non spécifié', '', 'informatique', 'formation', 'visualisation de données']
    comps = df['competences'].dropna().str.split(',').explode().str.strip().str.lower()
    comps = comps[~comps.isin(a_exclure) & (comps != '')]
    result = comps.value_counts().head(20)
    return jsonify({
        "competences": [{"competence": k, "nb_mentions": int(v)} for k, v in result.items()]
    })

@app.route('/api/evolution')
def evolution():
    data = df.dropna(subset=['mois'])
    result = data.groupby(data['mois'].dt.to_period('M')).size()
    return jsonify({
        "evolution": [{"mois": str(k), "nb_offres": int(v)} for k, v in result.items()]
    })

if __name__ == '__main__':
    app.run(debug=True)
