FROM alpine:3.18 as builder

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir ansible ansible-lint yamllint

WORKDIR /app

COPY ansible.cfg .
COPY inventory/hosts.ini ./inventory/
COPY playbooks/ssh_audit.yml ./playbooks/
COPY roles/ssh_audit/ ./roles/ssh_audit/
COPY requirements.txt .

RUN pip3 install -r requirements.txt

FROM alpine:3.18

RUN apk add --no-cache python3 jq && \
    rm -rf /var/cache/apk/*

COPY --from=builder /usr/lib/python3.11/site-packages/ /usr/lib/python3.11/site-packages/
COPY --from=builder /usr/bin/ansible* /usr/bin/
COPY --from=builder /app/ /app/

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]