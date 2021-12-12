const url = new URL(window.location.href)
const id = url.searchParams.get('id');

var idField = document.querySelector('h1');
idField.textContent = id;

var stat = document.querySelector('status');
var statProcessing = newElement('p', '분석 중입니다...');
stat.appendChild(statProcessing);

// API to recommend server
const recommendRequestURL = 'http://49.247.26.236:8000/api/rec/' + id; // server API
var recommendRequest = new XMLHttpRequest();
recommendRequest.open('GET', recommendRequestURL);
recommendRequest.responseType = 'json';
recommendRequest.send();

recommendRequest.onload = function() {
    const json = recommendRequest.response;
    const code = json['code'];
    //console.log(json);

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
    var num = 6 - (tier % 5 ? tier % 5 : 5);
    if(tier <=  0) return "unranked";
    if(tier <=  5) return "bronze" + num;
    if(tier <= 10) return "silver" + num;
    if(tier <= 15) return "gold" + num;
    if(tier <= 20) return "platinum" + num;
    if(tier <= 25) return "diamond" + num;
    if(tier <= 30) return "ruby" + num;
    return "unranked";
}

function loadStatus(json) {
    const user = json['user'];
    const tag = json['tag'];
    const problems = json['problems'];
    stat.removeChild(statProcessing);

    // load user info ////////////////////////////////////////////////////

    // API to solved.ac
    const solvedRequestURL = 'https://solved.ac/api/v3/user/show?handle=' + id;
    var solvedRequest = new XMLHttpRequest();
    solvedRequest.open('GET', solvedRequestURL);
    solvedRequest.responseType = 'json';
    solvedRequest.send();

    solvedRequest.onload = function() {
        const json = solvedRequest.response;
        //console.log(json);

        var handleTier = document.querySelector('img#userTierImg');
        handleTier.src = "/assets/solved-ac-emoji/" + tierChar(json['tier']) + ".png";

        idField.innerHTML = "<a href=" + "https://acmicpc.net/user/" + id + ">" + id + "</a>";

        var userInfo = document.getElementsByTagName('user-info')[0];

        var userSchool = document.createElement('div');
        userSchool.setAttribute('id', 'user-school');
        userSchool.setAttribute('class', 'flexwrap');

        var schoolImg = document.createElement('img');
        schoolImg.setAttribute('id', 'schoolImg');
        schoolImg.setAttribute('src', '/assets/106-Book.png');
        userSchool.appendChild(schoolImg);

        for(let organization of json['organizations']) {
            var schoolName = document.createElement('span');
            schoolName.textContent = organization['name'];
            userSchool.appendChild(schoolName);
        }

        userInfo.appendChild(userSchool);

        var userSolved = document.createElement('div');
        userSolved.setAttribute('id', 'user-solved');

        var ranking = document.createElement('span');
        ranking.innerHTML = "<b>" + json['rank'] + "</b> 위";
        userSolved.appendChild(ranking);

        var solved = document.createElement('span');
        solved.innerHTML = "<b>" + json['solvedCount'] + "</b> 문제 해결";
        userSolved.appendChild(solved);

        var rating = document.createElement('span');
        rating.innerHTML = "Rating <b>" + json['rating'] + "</b>";
        userSolved.appendChild(rating);

        userInfo.appendChild(userSolved);
    }
    /////////////////////////////////////////////////////////////////////

    // recommend result

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
        var problemLink = newElement('a', problem['id'] + '번 - ' + problem['name']);
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
            var item = newElement('li');
            item.setAttribute('class', 'li-inline');
            var tierImg = newElement('img');
            tierImg.setAttribute("class", "problemTierImge");
            tierImg.setAttribute("src", "/assets/solved-ac-emoji/" + tierChar(problem["tier"]) + ".png");
            item.appendChild(tierImg);
            var problemLink = newElement('a', problem['id'] + '번 - ' + problem['name']);
            problemLink.setAttribute('href', "https://icpc.me/" + problem['id']);
            item.appendChild(problemLink);
            problemsList.appendChild(item);
        }
        
        flexBox.appendChild(newElement('h3', tags));
        flexBox.appendChild(problemsList);
        
    }
    stat.appendChild(flexBox);
    stat.appendChild(newElement('br'));
}