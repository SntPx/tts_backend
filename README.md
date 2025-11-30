# tts_backend
<a href="https://github.com/SntPx/tts_backend/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/SntPx/tts_backend?color=blue"></a>

A quick TTS backend for my web app, relying on [Kokoro](https://github.com/hexgrad/kokoro).
It leverages Traefik (reverse proxy), Minio (S3 local server), and PostgreSQL, all of it containerized.

### Requirements
This was all developed and tested with:
* Docker 28.x

### Setup process
* Install Docker
* Clone the repository on your system
* Setup your environment variables
  * ```
    cp .env.example .env
    ```  
  * Modify .env accordingly to match your desired environment
  * Build and launch containers
    * ```
      docker compose up -d --build
      ```
      If the build process aborts because of a lack of space on your device, please use and modify TMPDIR in DockerFile,
      and/or modify /etc/docker/daemon.json:
      ```
      {
      "data-root": "/path/to/bigger/device"
      }
      ```
* Generate an augmented json representation of the irregular verbs, from container ```api```
  * ```
    python utils/augment_verbs.py IrregularVerbs.json AugmentedIrregularVerbs.json
    ```
* Generate the audio files corresponding to each form of the verbs, in both gb and us variants,from container ```api```
  * ```
    PYTHONPATH=/app python utils/generate_audio_files.py -i IrregularVerbs.json
    ```
* Populate the PostgreSQL database, from container ```api```
  * ```
    python scripts/import_audio_minio.py
    ```
* Ask for your certificates, modify your nginx configuration accordingly and reload nginx.

**Congratulations!** You have just set your TTS backend up.
Browse to ```https://api.yourdomain.tld/``` or ```https://audio.yourdomain.tld/``` 

### Troubleshooting
If your containers cannot connect to the Internet, either during the building stage or when you try to generate the
audio files, it is very likely that your firewall is blocking requests from and to your containers.
You'll then need to modify your firewall rules to let traffic from and to br-* (all containers have an internal name
starting with br-) and from and to docker0.
If your system uses nftables add the following lines to /etc/nftables in your forward chain in your inet filer table,
after the global drop policy:
```
  # Docker -> Internet
  iifname "br-*" oifname != "br-*" accept
  iifname "docker0" oifname != "docker0" accept
  iifname != "br-*" oifname "br-*" ct state established,related accept
  iifname != "docker0" oifname "docker0" ct state established,related accept
```
Then restart nftables:
```
sudo systemctl restart nftables
```