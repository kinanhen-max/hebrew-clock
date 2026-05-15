<!DOCTYPE html>
<html lang="he">
<head>
<meta charset="UTF-8">
<title>שעון עברי - מוקאפ</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #2a2a2a;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
  }
  .device {
    background: #e8e4db;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 0 0 2px #c5c0b5, 0 20px 60px rgba(0,0,0,0.5);
  }
  .screen {
    width: 640px;
    height: 384px;
    background: #f0ece3;
    position: relative;
    overflow: hidden;
  }
  .screen::before {
    content: '';
    position: absolute;
    inset: 6px;
    border: 2px solid #1a1a1a;
    pointer-events: none;
    z-index: 10;
  }
  .screen::after {
    content: '';
    position: absolute;
    inset: 13px;
    border: 1px solid #1a1a1a;
    pointer-events: none;
    z-index: 10;
  }

  /* Time center */
  .time-area {
    position: absolute;
    top: 20px; left: 0; right: 0; bottom: 90px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    direction: rtl;
  }
  .time-main   { font-size: 72px; font-weight: bold; color: #111; line-height: 1.1; font-family: 'Times New Roman', serif; }
  .time-min    { font-size: 56px; font-weight: bold; color: #111; line-height: 1.1; font-family: 'Times New Roman', serif; }
  .time-period { font-size: 34px; color: #222; margin-top: 6px; font-family: 'Times New Roman', serif; }

  /* Bottom bar — LTR: [analog] | [weather on RIGHT] */
  .bottom-bar {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 88px;
    border-top: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    direction: ltr;
  }

  /* Left side: analog clock */
  .left-side {
    display: flex;
    align-items: center;
    gap: 0;
  }

  .analog { width: 64px; height: 64px; flex-shrink: 0; }
  .divider { width: 1px; height: 52px; background: #bbb; margin: 0 20px; }

  /* Right side: weather */
  .right-side {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .wi { width: 52px; height: 52px; }
  .wtemp { font-size: 38px; font-weight: bold; color: #111; font-family: 'Times New Roman', serif; line-height: 1; }
  .wdesc { font-size: 15px; color: #444; font-family: 'Times New Roman', serif; margin-top: 3px; }
</style>
</head>
<body>

<div class="device">
  <div class="screen">

    <div class="time-area">
      <div class="time-main">שְׁתַּיִם עֶשְׂרֵה</div>
      <div class="time-min">וָחֵצִי</div>
      <div class="time-period">בַּצָּהֳרַיִם</div>
    </div>

    <div class="bottom-bar">

      <!-- LEFT: analog clock -->
      <div class="left-side">
        <svg class="analog" viewBox="0 0 100 100" fill="none" stroke="#111" stroke-linecap="round">
          <circle cx="50" cy="50" r="44" stroke-width="2.5"/>
          <line x1="50" y1="10" x2="50" y2="18" stroke-width="2.5"/>
          <line x1="90" y1="50" x2="82" y2="50" stroke-width="2.5"/>
          <line x1="50" y1="90" x2="50" y2="82" stroke-width="2.5"/>
          <line x1="10" y1="50" x2="18" y2="50" stroke-width="2.5"/>
          <line x1="74" y1="14" x2="71" y2="19" stroke-width="1.5"/>
          <line x1="86" y1="26" x2="81" y2="29" stroke-width="1.5"/>
          <line x1="86" y1="74" x2="81" y2="71" stroke-width="1.5"/>
          <line x1="74" y1="86" x2="71" y2="81" stroke-width="1.5"/>
          <line x1="26" y1="86" x2="29" y2="81" stroke-width="1.5"/>
          <line x1="14" y1="74" x2="19" y2="71" stroke-width="1.5"/>
          <line x1="14" y1="26" x2="19" y2="29" stroke-width="1.5"/>
          <line x1="26" y1="14" x2="29" y2="19" stroke-width="1.5"/>
          <line x1="50" y1="50" x2="53" y2="23" stroke-width="4" stroke-linecap="round"/>
          <line x1="50" y1="50" x2="50" y2="78" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="50" cy="50" r="3.5" fill="#111" stroke="none"/>
        </svg>
        <div class="divider"></div>
      </div>

      <!-- RIGHT: weather icon + temp + desc -->
      <div class="right-side">
        <div>
          <div class="wtemp">28°</div>
          <div class="wdesc">מעונן חלקי</div>
        </div>
        <svg class="wi" viewBox="0 0 50 50" fill="none" stroke="#111" stroke-width="2.5" stroke-linecap="round">
          <circle cx="17" cy="19" r="8"/>
          <line x1="17" y1="5" x2="17" y2="2"/>
          <line x1="17" y1="33" x2="17" y2="36"/>
          <line x1="3" y1="19" x2="0" y2="19"/>
          <line x1="31" y1="19" x2="34" y2="19"/>
          <line x1="7" y1="9" x2="4" y2="6"/>
          <line x1="27" y1="9" x2="30" y2="6"/>
          <path d="M22 35 Q16 35 16 29 Q16 24 22 24 Q24 18 30 18 Q38 18 38 26 Q42 26 42 31 Q42 35 37 35 Z" fill="#f0ece3" stroke="#111"/>
        </svg>
      </div>

    </div>
  </div>
</div>

</body>
</html>
