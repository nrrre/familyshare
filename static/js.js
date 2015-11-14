function showDiv(share_id){

  if (!document.getElementById("reply_content")) {

    var reply_content=document.createElement("textarea");
    var reply_submit=document.createElement("a");
    var link_name document.createTextNode("submit");
    var reply = document.getElementById("reply");

    reply_content.id="reply_content";
    reply_submit.href="/reply/" + share_id;

    reply.appendChild(reply_content);
    reply.appendChild(reply_submit);
    reply_submit.appendChild(link_name);
  
  }else{
    alert("test");
  }
}