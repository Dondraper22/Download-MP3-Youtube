YouTube to MP3 Downloader — README

Este programa permite baixar vídeos do YouTube e convertê-los diretamente para MP3 com interface gráfica moderna, usando Tkinter + ttkbootstrap e yt-dlp.

📌 Funcionalidades

Baixar múltiplos URLs do YouTube simultaneamente

Conversão automática para MP3 em 192 kbps

Interface gráfica moderna com tema darkly

Seleção de pasta de saída

Carregamento de lista de URLs a partir de arquivo .txt

Barra de progresso total

Barras de progresso individuais para cada download

Log detalhado em tempo real

Execução dos downloads em thread separada (não trava a interface)

📝 Requisitos

Certifique-se de instalar as dependências:

pip install yt-dlp ttkbootstrap


É necessário também ter o FFmpeg instalado no sistema.
Baixe em: https://ffmpeg.org/download.html

e adicione ao PATH.

▶️ Como usar

Abra o programa.

Cole os URLs dos vídeos do YouTube, um por linha, ou carregue um arquivo TXT com os links.

Escolha o diretório onde deseja salvar os MP3.

Clique em “Baixar MP3s”.

Acompanhe o progresso pelas barras individuais e o progresso geral.

📁 Estrutura dos arquivos gerados

Os arquivos são salvos com o seguinte padrão:

/diretorio_escolhido/
    Título do Vídeo.mp3

⚙️ Como funciona internamente

O programa utiliza:

yt-dlp para baixar o áudio em melhor qualidade

FFmpegExtractAudio para converter para MP3

Tkinter + ttkbootstrap para interface gráfica

Progress hooks do yt-dlp para atualizar a barra de progresso

Threading para evitar travamentos na interface

🧾 Licença

Você pode modificar, distribuir e usar o código livremente para fins pessoais.
