const url = new URL(window.location.href)
const id = url.searchParams.get('id');

var idField = document.querySelector('h1');
idField.textContent = id;

var stat = document.querySelector('status');
var statProcessing = newElement('p', '분석 중입니다...');
stat.appendChild(statProcessing);

const requestURL = 'http://49.247.26.236:8000/api/rec/' + id; // server API
var request = new XMLHttpRequest();
request.open('GET', requestURL);
request.responseType = 'json';
request.send();

request.onload = function() {
    const json = request.response;
    const code = json['code'];
    console.log(json);

    if(code == 200) loadStatus(json);
    else loadError();
}

function newElement(tag, textContent = '', id = '') {
    var element = document.createElement(tag);
    if (textContent != '') element.textContent = textContent;
    if (id != '') element.setAttribute('id', id);
    return element;
}

function loadError() {
    stat.removeChild(statProcessing);
    stat.appendChild(newElement('h1', '404'));
    stat.appendChild(newElement('p', '다음 중 하나의 오류가 발생했습니다.'));
    var error = newElement('ul');
    error.appendChild(newElement('li', '사용자 ID의 형식이 올바르지 않거나, 해당 사용자가 존재하지 않습니다.'));
    error.appendChild(newElement('li', '사용자가 solved.ac에 로그인한 적이 없거나, BOJ에서 정보 공개를 동의한 적이 없습니다.'));
    stat.appendChild(error);
}

function tierChar(tier) {
    if(tier <=  0) return "unranked";
    if(tier <=  5) return "bronze" + (tier % 5 + 1);
    if(tier <= 10) return "silver" + (tier % 5 + 1);
    if(tier <= 15) return "gold" + (tier % 5 + 1);
    if(tier <= 20) return "platinum" + (tier % 5 + 1);
    if(tier <= 25) return "diamond" + (tier % 5 + 1);
    if(tier <= 30) return "ruby" + (tier % 5 + 1);
    return "unranked";
}

function loadStatus(json) {
    const user = json['user'];
    const tag = json['tag'];
    const problems = json['problems'];

    // load user info ////////////////////////////////////////////////////
    var handleTier = document.querySelector('img#userTierImg');
    handleTier.src = "/assets/solved-ac-emoji/" + tierChar(user['tier']) + ".png";

    var userInfo = document.getElementsByTagName('user-info')[0];
    userInfo.style.display = 'block';
    for(let info of ['ranking', 'solved', 'rating']) {
        var obj = document.querySelector('#' + info);
        obj.textContent = user[info];
    }

    // clear status
    stat.removeChild(statProcessing);

    // load result ////////////////////////////////////////////////////////
    var userArea = document.createElement('div');
    userArea.setAttribute('id', 'userArea');
    
    var pieChart = document.createElement('img');
    pieChart.src = '/assets/pie-chart.png';
    userArea.appendChild(pieChart);
    
    stat.appendChild(newElement('h3', "▷ 파이차트 추후 지원 예정"));
    stat.appendChild(userArea);


    var flexBox = newElement('div');
    flexBox.setAttribute('class', 'flexwrap');

    flexBox.appendChild(newElement('h3', "Strong Area"));

    var strongTagList = newElement('ul'); 
    for (it of tag['strong'])
        strongTagList.appendChild(newElement('li', it));
    flexBox.appendChild(strongTagList);

    flexBox.appendChild(newElement('h3', "Weak Area"));

    var weakTagList = newElement('ul'); 
    for (it of tag['weak'])
        weakTagList.appendChild(newElement('li', it));
    flexBox.appendChild(weakTagList);

    stat.appendChild(flexBox);

    ////////////////////////////////////////////////////////////////////////////////

    stat.appendChild(newElement('br'));
    stat.appendChild(newElement('h1', "Best Pick"));
    var description = newElement('p', "전반적인 실력 향상을 위해 추천하는 문제입니다.");
    description.style.color = 'grey';
    stat.appendChild(description);  

    var problemsList = newElement('ul');
    for (problem of problems['all']) {
        var flexBox = newElement('div');
        flexBox.setAttribute('class', 'li-inline');
        var tierImg = newElement('img');
        tierImg.setAttribute("class", "problemTierImge");
        tierImg.setAttribute("src", "/assets/solved-ac-emoji/" + tierChar(problem["tier"]) + ".png");
        flexBox.appendChild(tierImg);
        var problemLink = newElement('a', "icpc.me/" + problem['id']);
        problemLink.setAttribute('href', "https://icpc.me/" + problem['id']);
        flexBox.appendChild(problemLink);
        var item = newElement('li');
        item.appendChild(flexBox);
        problemsList.appendChild(item);
    }
    stat.appendChild(problemsList);
    
    stat.appendChild(newElement('br'));
    stat.appendChild(newElement('br'));
    stat.appendChild(newElement('h1', "Advanced Pick"));
    var description = newElement('p', "태그별 실력 향상을 위해 추천하는 문제입니다.");
    description.style.color = 'grey';
    stat.appendChild(description); 

    flexBox = newElement('div');
    flexBox.setAttribute('class', 'flex');
    for(tags of Object.keys(problems)) {
        if(tags == 'all') continue;
    
        var problemsList = newElement('ul');
        for (problem of problems[tags]) {
            var flexBox2 = newElement('div');
            flexBox2.setAttribute('class', 'li-inline');
            var tierImg = newElement('img');
            tierImg.setAttribute("class", "problemTierImge");
            tierImg.setAttribute("src", "/assets/solved-ac-emoji/" + tierChar(problem["tier"]) + ".png");
            flexBox2.appendChild(tierImg);
            var problemLink = newElement('a', "icpc.me/" + problem['id']);
            problemLink.setAttribute('href', "https://icpc.me/" + problem['id']);
            flexBox2.appendChild(problemLink);
            var item = newElement('li');
            item.appendChild(flexBox2);
            problemsList.appendChild(item);
        }
        
        flexBox.appendChild(newElement('h3', tags));
        flexBox.appendChild(problemsList);
        
    }
    stat.appendChild(flexBox);
    stat.appendChild(newElement('br'));
}
