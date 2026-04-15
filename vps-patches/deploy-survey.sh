#!/bin/bash
# Deploy sow-survey-review endpoint to VPS
# Run: scp vps-patches/sow-survey-endpoint.py root@187.124.240.101:/root/sow_survey_endpoint.py
#      scp vps-patches/deploy-survey.sh root@187.124.240.101:/root/deploy_survey.sh
#      ssh root@187.124.240.101 'bash /root/deploy_survey.sh'

cd /root/podio-sync
cp server.py server.py.bak3

# Find if __name__ line and insert endpoint before it
python3 -c "
with open('server.py','r') as f: lines = f.readlines()
for i, line in enumerate(lines):
    if line.strip().startswith('if __name__'):
        with open('/root/sow_survey_endpoint.py','r') as f2: new_code = f2.read()
        lines.insert(i, new_code + '\n')
        with open('server.py','w') as f: f.writelines(lines)
        print('Endpoint added at line', i)
        break
"

# Also deploy the v2 design compare endpoint if not already done
if [ -f /root/deploy_v2.sh ]; then
    echo "Note: run deploy_v2.sh separately if needed"
fi

systemctl restart aveyo-server
sleep 2
systemctl status aveyo-server --no-pager | head -5
echo "SURVEY ENDPOINT DEPLOYED"
