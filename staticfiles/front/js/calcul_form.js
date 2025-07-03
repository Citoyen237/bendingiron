document.addEventListener("DOMContentLoaded", () => {
    // Map des abréviations aux noms des champs dans le formulaire
    const dimensionMap = {
        lon: 'Longueur du coté',   // Abbréviation pour Longueur
        lar: 'Largeur du coté',    // Abbréviation pour Largeur
        c: 'Longueur du coté',    // Abbréviation pour Hauteur
        lonf: 'Longueur de fin'   // Abbréviation pour Diamètre
    };

    // Champs de résultat
    const cadreLongueurField = document.getElementById("cadreLongueur");
    const quantiteField = document.getElementById("quantiteCadre");
    const prixUnitaireField = document.getElementById("prixUnitaire");
    const prixTotalField = document.getElementById("prixTotal");

    // Fonction pour récupérer les valeurs des dimensions à partir des champs du formulaire
    const getDimensionsByAbbreviation = () => {
        const dimensions = {};
        // Parcourir la carte des abréviations et récupérer les valeurs des champs correspondants
        for (const [abbreviation, fieldName] of Object.entries(dimensionMap)) {
            const input = document.querySelector(`[name="${fieldName}"]`);
            const value = input ? parseFloat(input.value || 0) : 0;
            dimensions[abbreviation] = value;
        }
        return dimensions;
    };

    // Fonction pour calculer la longueur du cadre en utilisant la formule
    const calculateCadreLongueur = (dimensions, formula) => {
        try {
            // Utiliser eval pour évaluer la formule avec les dimensions
            const result = eval(formula);  // Utilisation de eval avec prudence
            cadreLongueurField.value = result.toFixed(2);
            return result;
        } catch (error) {
            console.error("Erreur dans la formule :", error);
            cadreLongueurField.value = "Erreur";
            return 0;
        }
    };

    // Fonction pour calculer le prix unitaire (exemple)
    const calculatePrixUnitaire = (longueur) => {
        const prixUnitaire = longueur * 10; // Exemple : 10 est un coût fixe par unité de longueur
        prixUnitaireField.value = prixUnitaire.toFixed(2);
        return prixUnitaire;
    };

    // Fonction pour calculer le prix total en fonction de la quantité
    const calculatePrixTotal = (prixUnitaire, quantite) => {
        const prixTotal = prixUnitaire * quantite;
        prixTotalField.value = prixTotal.toFixed(2);
    };

    // Fonction pour mettre à jour les champs en fonction des dimensions saisies
    const updateFields = () => {
        const dimensions = getDimensionsByAbbreviation();  // Obtenir les dimensions
        const formula = "dimensions['L'] + dimensions['l'] * 2";  // Exemple de formule à ajuster

        const longueur = calculateCadreLongueur(dimensions, formula);
        const prixUnitaire = calculatePrixUnitaire(longueur);
        calculatePrixTotal(prixUnitaire, parseInt(quantiteField.value || 1, 10));
    };

    // Initialiser les champs dès le chargement
    updateFields();

    // Ajouter un événement pour recalculer les valeurs chaque fois qu'un champ est modifié
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', updateFields);
    });
});
