from music_analyzer import MusicAnalyzer

# Lady Ethereal 테스트
print("\n=== 롱 노트 생성 테스트 ===\n")

analyzer = MusicAnalyzer('music/Lady Ethereal.mp3')
analyzer.load_and_analyze()

chart = analyzer.generate_chart('normal', 3.0)

print(f"\n총 노트: {len(chart)}")
print(f"일반 노트: {sum(1 for n in chart if n['type'] == 'normal')}")
print(f"롱 노트: {sum(1 for n in chart if n['type'] == 'long')}")

# 롱 노트 샘플 출력
long_notes = [n for n in chart if n['type'] == 'long']
if long_notes:
    print(f"\n롱 노트 샘플 (처음 5개):")
    for i, note in enumerate(long_notes[:5]):
        print(f"  {i+1}. 시간: {note['time']:.2f}초, 길이: {note['duration']:.2f}초")
