FROM python:alpine3.16
 
WORKDIR /home/app
 
# Environment variable for accepting EULA
ENV ACCEPT_EULA=Y
 
# Update and install necessary packages
RUN apk update && apk add --no-cache curl gcc g++ unixodbc-dev gnupg
 
# Determine architecture and download appropriate packages
RUN case $(uname -m) in \
        x86_64)   architecture="amd64" ;; \
        arm64)   architecture="arm64" ;; \
        *) architecture="unsupported" ;; \
    esac \
    && if [ "$architecture" = "unsupported" ]; then \
        echo "Alpine architecture $(uname -m) is not currently supported."; \
        exit 1; \
    fi \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.10.5.1-1_amd64.apk \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.10.1.1-1_amd64.apk \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.10.5.1-1_amd64.sig \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.10.1.1-1_amd64.sig \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --import - \
    && gpg --verify msodbcsql17_17.10.5.1-1_$architecture.sig msodbcsql17_17.10.5.1-1_$architecture.apk \
    && gpg --verify mssql-tools_17.10.1.1-1_$architecture.sig mssql-tools_17.10.1.1-1_$architecture.apk \
    && apk add --allow-untrusted msodbcsql17_17.10.5.1-1_$architecture.apk \
    && apk add --allow-untrusted mssql-tools_17.10.1.1-1_$architecture.apk
 
COPY requirements.txt .
RUN pip3 install --upgrade pip &&pip3 install -r requirements.txt && pip3 install gunicorn
 
COPY . .
 
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--access-logfile", "-", "--error-logfile", "-"]