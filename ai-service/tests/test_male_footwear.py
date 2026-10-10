"""Footwear advice and scores must match the visible male wardrobe."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.api.routers.wardrobe_remix import RemixBody, _score
from app.models import Colors, OutfitState
from app.engine.rules import evaluate


@pytest.mark.parametrize('rule_id,shoes,occasion', [
    ('R45', 'dep', 'tet'),
    ('R46', 'dep', 'dao_pho'),
    ('R47', 'giay_the_thao', 'dam_cuoi'),
    ('R48', 'khong', 'dam_cuoi'),
    ('R57', 'khong', 'tet'),
])
def test_footwear_advice_matches_gender_without_changing_rule(catalog, rule_id, shoes, occasion):
    rule = next(r for r in catalog.rules if r['id'] == rule_id)
    original = deepcopy(rule)
    state = OutfitState(garment='ao_dai', gender='nam', occasion=occasion, style='truyen_thong',
                        colors=Colors(main='do_son', bottom='trang_nga'),
                        bottom='quan_dai_suong', shoes=shoes)
    male = evaluate(state, [rule])[0]
    assert 'giày da' in male.suggestion.text
    assert 'búp bê' not in male.suggestion.text
    state.gender = 'nu'
    female = evaluate(state, [rule])[0]
    assert female.suggestion.text == rule['suggestion']['text']
    assert male.id == female.id and male.level == female.level
    assert rule == original


def payload(shoes, event='TET', shirt='teal', context=None):
    return dict(outfitCode='AO_DAI', colorCode='RED', styleCode='TRADITIONAL', eventCode=event,
                accessories=[], context=context,
                wardrobe={'character': 'male', 'selection': {
                    'shirt': shirt, 'pants': 'wide-charcoal', 'shoes': shoes, 'accessories': {}}})


@pytest.mark.parametrize('shoes', ['dep-le', 'dep-crocs'])
@pytest.mark.parametrize('shirt', ['teal', 'ngu-than', 'ba-ba'])
@pytest.mark.parametrize('event', ['TET', 'GRADUATION', 'CULTURAL_EVENT', 'FESTIVAL'])
def test_male_sandals_on_formal_occasions_share_score_and_advice(client, catalog, shoes, shirt, event):
    body = payload(shoes, event, shirt)
    quick = client.post('/ai/wardrobe-score', json=body)
    review = client.post('/ai/wardrobe-review', json=body)
    assert quick.status_code == review.status_code == 200, review.text
    result, current = quick.json(), review.json()['current']
    check = next(e for e in result['checks'] if e['ruleId'] == 'R45')
    reviewed = next(e for e in current['evaluations'] if e['id'] == 'R45')
    assert check['suggestion'] == reviewed['suggestion']['text']
    assert 'giày da' in check['suggestion'] and 'búp bê' not in check['suggestion']
    assert result['score'] == current['scoreCard']['total'] <= 45
    assert result['level'] == 'HIGH_RISK' and review.json()['verdict'] == 'chua_hop'
    remix = RemixBody(**body, prompt='Giữ bộ hiện tại', options={
        'outfits': [], 'pants': [], 'shoes': [], 'accessories': []})
    assert _score(remix, remix.wardrobe.selection, SimpleNamespace(catalog=catalog))[1].total == result['score']


@pytest.mark.parametrize('shoes', ['dep-le', 'dep-crocs'])
def test_male_casual_sandals_and_rain_use_known_context(client, shoes):
    def checks(context):
        response = client.post('/ai/wardrobe-score', json=payload(shoes, 'PHOTOSHOOT', context=context))
        assert response.status_code == 200, response.text
        return {e['ruleId']: e for e in response.json()['checks']}

    casual = checks(None)
    assert 'R46' in casual and 'R45' not in casual and 'R62' not in casual
    assert 'giày da' in casual['R46']['suggestion']
    assert 'R62' not in checks({'weather': 'mua'})
    assert 'R62' not in checks({'weather': 'mua', 'setting': 'trong_nha'})
    for setting in ('ngoai_troi', 'ca_hai'):
        assert {'R46', 'R62'} <= checks({'weather': 'mua', 'setting': setting}).keys()


@pytest.mark.parametrize('shoes', ['loafers', 'giay-ta', 'hai-theu', 'guoc'])
def test_formal_male_footwear_does_not_trigger_sandal_rules(client, shoes):
    response = client.post('/ai/wardrobe-score', json=payload(shoes))
    assert response.status_code == 200, response.text
    assert not {'R45', 'R46', 'R62'} & {e['ruleId'] for e in response.json()['checks']}
