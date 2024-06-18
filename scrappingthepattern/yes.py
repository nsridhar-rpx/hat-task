from google_patent_scraper import scraper_class
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# ~ Initialize scraper class ~ #
scraper=scraper_class()

# ~ Add patents to list ~ #
scraper.add_patents('US2668287A')
scraper.add_patents('US266827A')

# ~ Scrape all patents ~ #
scraper.scrape_all_patents()

# ~ Get results of scrape ~ #
patent_1_parsed = scraper.parsed_patents['US2668287A']
patent_2_parsed = scraper.parsed_patents['US266827A']

# ~ Print inventors of patent US2668287A ~ #
for inventor in json.loads(patent_1_parsed['inventor_name']):
  print('Patent inventor : {0}'.format(inventor['inventor_name']))













from flask import Blueprint, request, jsonify
from your_project.app.extensions import db
from your_project.app.models.patent import Patent
from apscheduler.schedulers.background import BackgroundScheduler
from your_project.app.schemas import PatentSchema
from datetime import datetime, timedelta
patent_schema = PatentSchema()
from marshmallow import ValidationError


patents_bp = Blueprint('patents', __name__)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()


@scheduler.scheduled_job('interval', minutes=30)  
def check_for_patent_updates():
    patents = Patent.query.all()
    for patent in patents:
        if patent.details_have_changed():  
            patent.update_details()  

@patents_bp.route('/patents', methods=['GET'])
def get_patent_details():
    patnums = request.args.getlist('patnums[]')
    patents = Patent.get_patents(patnums)
    if patents:
        
        result = patent_schema.dump(patents)
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No patents found for the given application numbers'}), 404

@patents_bp.route('/patents/delete', methods=['DELETE'])
def delete_patent_details():
    patnum = request.args.get('patnum')
    if Patent.delete_patent(patnum):
        return jsonify({'message': f'Patent with application number {patnum} deleted successfully'}), 200
    else:
        return jsonify({'message': f'Patent with application number {patnum} not found'}), 404




@patents_bp.route('/patents/update', methods=['PUT'])
def update_patent_details():
    data = request.get_json()
    try:
        
        validated_data = patent_schema.load(data)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

    patnum = validated_data['application_number']
    if Patent.update_patent(patnum, validated_data):
        return jsonify({'message': f'Patent with application number {patnum} updated successfully'}), 200
    else:
        return jsonify({'message': f'Patent with application number {patnum} not found'}), 404
