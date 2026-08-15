// African Frame — shared content store
var STORAGE_KEY = "africanFrameContent";

var DEFAULT_CONTENT = {
    news: [
        { id: "n1", tag: "Industry", title: "Local Studio Announces Slate Of Five New Features", meta: "2 hrs ago · 4 min read" },
        { id: "n2", tag: "Casting", title: "Lead Role Recast Weeks Before Production Start", meta: "5 hrs ago · 3 min read" },
        { id: "n3", tag: "Festival", title: "Official Selection List Released For This Year's Festival", meta: "Yesterday · 6 min read" },
        { id: "n4", tag: "Streaming", title: "Platform Confirms Local Original Renewed For Season Two", meta: "Yesterday · 3 min read" },
    ],
    reviews: [
        { id: "r1", tag: "Drama", title: "A Quiet Return", blurb: "A patient, aching family drama that trusts its silences.", score: "9.1" },
        { id: "r2", tag: "Action", title: "Last Line Of Defence", blurb: "Big set pieces, thin plotting — style carries it most of the way.", score: "7.3" },
        { id: "r3", tag: "Comedy", title: "Wedding Season", blurb: "Sharp, warm, and unafraid to let a joke breathe.", score: "8.6" },
        { id: "r4", tag: "Horror", title: "The Nightwatch", blurb: "A strong first act that the back half can't sustain.", score: "6.2" },
    ],
    architecture: [
        { id: "a1", tag: "Design", title: "Set Design That Tells the Story", meta: "3 days ago · 5 min read" },
        { id: "a2", tag: "Technical", title: "How Camera Movement Shapes Emotion", meta: "1 week ago · 7 min read" },
        { id: "a3", tag: "Perspective", title: "The Architecture of Suspense in Horror", meta: "2 weeks ago · 6 min read" },
    ],
};

function getContent() {
    try {
        var raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return JSON.parse(JSON.stringify(DEFAULT_CONTENT));
        var parsed = JSON.parse(raw);
        return {
            news: Array.isArray(parsed.news) ? parsed.news : DEFAULT_CONTENT.news,
            reviews: Array.isArray(parsed.reviews) ? parsed.reviews : DEFAULT_CONTENT.reviews,
            architecture: Array.isArray(parsed.architecture) ? parsed.architecture : DEFAULT_CONTENT.architecture,
        };
    } catch (e) {
        console.error("Could not read saved content, using defaults.", e);
        return JSON.parse(JSON.stringify(DEFAULT_CONTENT));
    }
}

function saveContent(content) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(content));
}

function resetContent() {
    localStorage.removeItem(STORAGE_KEY);
}

function makeId(prefix) {
    return prefix + "_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}