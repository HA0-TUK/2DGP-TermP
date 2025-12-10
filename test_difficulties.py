from music_analyzer import MusicAnalyzer

songs = ['Lady Ethereal.mp3', 'M2U.mp3', 'Shaolin Warrior.mp3']

print("\n난이도별 노트 수 비교:")
print("=" * 70)

for song in songs:
    analyzer = MusicAnalyzer(f'music/{song}')
    analyzer.load_and_analyze()
    
    normal_chart = analyzer.generate_chart('normal', 3.0)
    hard_chart = analyzer.generate_chart('hard', 3.0)
    
    print(f"{song:25} | Normal: {len(normal_chart):4}개 | Hard: {len(hard_chart):4}개 | 차이: +{len(hard_chart) - len(normal_chart):4}개")

print("=" * 70)
