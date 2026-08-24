# radgram/cli.py
import argparse, json
from radgram.maestro.composer import compose, compose_to_db
from radgram.maestro.instruments_db import MaestroInstrumentManager
from radgram.catalog.db import Catalog
from radgram.artgen.cover_genai import generate_cover
from radgram.mastering.master import master_chain, trim
from radgram.core.drm import create_drm_package, verify_drm_package
from radgram.core.raddisk import export_raddisk
from radgram.vision.importer import import_music_source
from radgram.album.album_builder import create_album, add_track_file, album_from_sources, album_from_tracks
from radgram.pipeline.album_site import build_album_website
from radgram.stream.base64_stream import get_album_stream_manifest
from radgram.jam.session import create_jam, add_chord_event, add_note_event, list_jams

# Importações dos novos módulos de extração e OpenVINO
from radgram import InstrumentSampleSlicer, PhonemeExtractor, OpenVINOMusicCore

def print_json(data): print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser('radgram')
    ap.add_argument('--db', default='radgram.sqlite3', help='SQLite database path')
    sub=ap.add_subparsers(dest='cmd')
    sub.add_parser('init-db')
    c=sub.add_parser('compose')
    c.add_argument('--title',default='Untitled'); c.add_argument('--artist',default='Radgram AI'); c.add_argument('--album',default='RADGRAM Sessions')
    c.add_argument('--progression',nargs='*',default=['C','Am','F','G']); c.add_argument('--out',default='exports/song'); c.add_argument('--bpm',type=int,default=96)
    c.add_argument('--instrument', default='Piano'); c.add_argument('--save-db', action='store_true')
    addi=sub.add_parser('add-instrument'); addi.add_argument('name'); addi.add_argument('--family',default=''); addi.add_argument('--description',default=''); addi.add_argument('--midi-program',type=int); addi.add_argument('--volume',type=float,default=1.0); addi.add_argument('--pan',type=float,default=0.0)
    adds=sub.add_parser('add-sample'); adds.add_argument('instrument'); adds.add_argument('label'); adds.add_argument('wav_path'); adds.add_argument('--note',default=''); adds.add_argument('--chord',default=''); adds.add_argument('--library',default='radgram_library/instruments'); adds.add_argument('--no-copy',action='store_true')
    lp=sub.add_parser('list-instruments'); lp.add_argument('--samples', action='store_true'); lp.add_argument('--instrument')
    preset=sub.add_parser('preset'); preset.add_argument('name'); preset.add_argument('--style',default='cinematic'); preset.add_argument('--bpm',type=int,default=96); preset.add_argument('--key',default='C'); preset.add_argument('--progression', nargs='*', default=['C','Am','F','G']); preset.add_argument('--instruments', nargs='*', default=['Piano'])
    album=sub.add_parser('album-create'); album.add_argument('--artist',required=True); album.add_argument('--title',required=True); album.add_argument('--description',default=''); album.add_argument('--year',type=int,default=2026); album.add_argument('--genre',default='AI Music'); album.add_argument('--cover',default='')
    at=sub.add_parser('album-add-track'); at.add_argument('--album-guid',required=True); at.add_argument('--title',required=True); at.add_argument('--file',default=''); at.add_argument('--rad',default=''); at.add_argument('--number',type=int,default=1); at.add_argument('--author',default=''); at.add_argument('--bpm',type=int,default=96); at.add_argument('--key',default='C'); at.add_argument('--chords',nargs='*',default=['C','Am','F','G'])
    aft=sub.add_parser('album-from-tracks'); aft.add_argument('--artist',required=True); aft.add_argument('--title',required=True); aft.add_argument('tracks',nargs='+'); aft.add_argument('--out',default='exports/albums'); aft.add_argument('--genre',default='AI Music')
    afs=sub.add_parser('album-from-sheets'); afs.add_argument('--artist',required=True); afs.add_argument('--title',required=True); afs.add_argument('sources',nargs='+'); afs.add_argument('--out',default='exports/albums'); afs.add_argument('--instrument',default='Piano')
    sub.add_parser('library-list')
    site=sub.add_parser('album-website'); site.add_argument('--album-guid',required=True); site.add_argument('--out',default='exports/album_site')
    man=sub.add_parser('stream-manifest'); man.add_argument('--album-guid',required=True)
    rd=sub.add_parser('export-raddisk'); rd.add_argument('--album-guid',required=True); rd.add_argument('--out',required=True); rd.add_argument('--license',default='RADGRAM-DRM-DEMO')
    jam=sub.add_parser('jam-create'); jam.add_argument('--title',required=True); jam.add_argument('--description',default=''); jam.add_argument('--album-guid'); jam.add_argument('--bpm',type=int,default=96); jam.add_argument('--key',default='C')
    je=sub.add_parser('jam-add'); je.add_argument('--jam-guid',required=True); je.add_argument('--user',default='guest'); je.add_argument('--chord'); je.add_argument('--note'); je.add_argument('--bar',type=int,default=1); je.add_argument('--duration',type=float,default=1.0); je.add_argument('--instrument',default='Piano')
    sub.add_parser('jam-list')
    m=sub.add_parser('master'); m.add_argument('input'); m.add_argument('out')
    t=sub.add_parser('trim'); t.add_argument('input'); t.add_argument('out'); t.add_argument('--seconds',type=int,default=15)
    d=sub.add_parser('drm'); d.add_argument('input'); d.add_argument('out')
    i=sub.add_parser('import-source'); i.add_argument('source'); i.add_argument('--ocr', action='store_true'); i.add_argument('--lang', default='eng'); i.add_argument('--out')
    
    # NOVOS COMANDOS ADICIONADOS AO CLI
    es = sub.add_parser('extract-samples')
    es.add_argument('--input', required=True, help='Input audio file path (e.g., solo_guitar.wav)')
    es.add_argument('--instrument', required=True, help='Instrument name (e.g., Guitar, Sax)')
    es.add_argument('--output', required=True, help='Output directory for samples')

    ep = sub.add_parser('extract-phonemes')
    ep.add_argument('--input', required=True, help='Input vocal track path (.mp3 or .ogg)')
    ep.add_argument('--output', required=True, help='Output directory for phonemes')

    co = sub.add_parser('compose-openvino')
    co.add_argument('--prompt', required=True, help='Musical style prompt')
    co.add_argument('--device', default='CPU', help='Hardware device (CPU, GPU, NPU)')

    sub.add_parser('export-db-json')
    
    # COMANDO SERVE ATUALIZADO COM SUPORTE A API
    serve_parser = sub.add_parser('serve', help='Inicia a interface web ou o servidor da API')
    serve_parser.add_argument('--api', action='store_true', help='Inicia o servidor FastAPI (para curl/URL)')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Endereço de host')
    serve_parser.add_argument('--port', type=int, default=7860, help='Porta do servidor')
    
    args=ap.parse_args()
    
    if args.cmd=='init-db': Catalog(args.db); print(f'{args.db} created')
    elif args.cmd=='compose':
        if args.save_db:
            result=compose_to_db(args.title,args.artist,args.album,progression=args.progression,bpm=args.bpm,out_dir=args.out,instrument=args.instrument,db=args.db); result['cover']=generate_cover(args.title,args.artist,out=f'{args.out}/cover.png'); print_json(result)
        else:
            project,wav=compose(args.title,args.artist,progression=args.progression,bpm=args.bpm,out_dir=args.out); cover=generate_cover(args.title,args.artist,out=f'{args.out}/cover.png'); print_json({'rad':project.to_json(),'wav':str(wav),'cover':cover})
    elif args.cmd=='add-instrument': print_json({'instrument_guid':MaestroInstrumentManager(args.db).add_instrument(args.name,args.family,args.description,args.midi_program,args.volume,args.pan)})
    elif args.cmd=='add-sample': print_json({'sample_guid':MaestroInstrumentManager(args.db,args.library).install_sample(args.instrument,args.label,args.wav_path,note=args.note,chord=args.chord,copy=not args.no_copy)})
    elif args.cmd=='list-instruments':
        mgr=MaestroInstrumentManager(args.db); print_json(mgr.list_samples(args.instrument) if args.samples else mgr.list_instruments())
    elif args.cmd=='preset': print_json({'preset_guid':MaestroInstrumentManager(args.db).configure_preset(args.name,args.instruments,args.progression,args.style,args.bpm,args.key)})
    elif args.cmd=='album-create': print_json(create_album(args.db,args.artist,args.title,args.description,args.year,args.genre,args.cover))
    elif args.cmd=='album-add-track': print_json({'track_guid':add_track_file(args.db,args.album_guid,args.title,args.file,args.rad,args.number,args.author,args.bpm,args.key,args.chords)})
    elif args.cmd=='album-from-tracks': print_json(album_from_tracks(args.db,args.artist,args.title,args.tracks,args.out,args.genre))
    elif args.cmd=='album-from-sheets': print_json(album_from_sources(args.db,args.artist,args.title,args.sources,args.out,args.instrument))
    elif args.cmd=='library-list': print_json(Catalog(args.db).library())
    elif args.cmd=='album-website': print_json({'index':build_album_website(args.db,args.album_guid,args.out)})
    elif args.cmd=='stream-manifest': print_json(get_album_stream_manifest(args.db,args.album_guid))
    elif args.cmd=='export-raddisk': print_json(export_raddisk(args.db,args.album_guid,args.out,args.license))
    elif args.cmd=='jam-create': print_json({'jam_guid':create_jam(args.db,args.title,args.description,args.album_guid,args.bpm,args.key)})
    elif args.cmd=='jam-add':
        if args.chord: print_json({'event_guid':add_chord_event(args.db,args.jam_guid,args.user,args.chord,args.bar,args.instrument)})
        elif args.note: print_json({'event_guid':add_note_event(args.db,args.jam_guid,args.user,args.note,args.duration,args.instrument)})
        else: print_json({'error':'use --chord or --note'})
    elif args.cmd=='jam-list': print_json(list_jams(args.db))
    elif args.cmd=='master': print(master_chain(args.input,args.out))
    elif args.cmd=='trim': print(trim(args.input,args.out,duration=args.seconds))
    elif args.cmd=='drm': print(create_drm_package(args.input,args.out), verify_drm_package(args.out))
    elif args.cmd=='import-source':
        data=import_music_source(args.source, ocr=args.ocr, lang=args.lang); text=json.dumps(data, indent=2, ensure_ascii=False)
        if args.out: open(args.out,'w',encoding='utf-8').write(text); print(args.out)
        else: print(text)  
    elif args.cmd=='extract-samples':
        slicer = InstrumentSampleSlicer()
        print_json(slicer.slice_instrument_track(args.input, args.instrument, args.output))
    elif args.cmd=='extract-phonemes':
        extractor = PhonemeExtractor()
        print_json(extractor.extract_phonemes_from_audio(args.input))
    elif args.cmd=='compose-openvino':
        core = OpenVINOMusicCore(device=args.device)
        print_json(core.optimize_and_run_generation(args.prompt, style="OpenVINO Generated"))

    elif args.cmd=='export-db-json': print_json(Catalog(args.db).export_json())
    elif args.cmd=='serve':
        if args.api:
            import uvicorn
            print(f"Iniciando API Radgram (FastAPI) em http://{args.host}:{args.port}...")
            uvicorn.run("radgram.web.api:app", host=args.host, port=args.port, reload=True)
        else:
            from radgram.web.app import run
            run()
    else: ap.print_help()

if __name__=='__main__': main()