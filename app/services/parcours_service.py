# def remove_site_from_parcours(parcours_id: int, site_id: int):
#     parcours = ParcoursModel.get_by_id(parcours_id)
#     nb_sites_precedent = len(parcours['sites'])

#     ParcoursModel.remove_site(parcours_id, site_id)
#     ParcoursModel.update(parcours_id, nb_sites_precedent=nb_sites_precedent)