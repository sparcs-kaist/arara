namespace py arara_thrift

////////////////////////////////////////
// Section 1 : Exception Definition
////////////////////////////////////////

exception InternalError {
    1: optional string why
}

exception InvalidOperation {
    1: string why
}

exception NotLoggedIn {

}

////////////////////////////////////////
// Section 2 : Data Type Definition
////////////////////////////////////////

typedef i32 id_t

struct VisitorCount {
    1: i32 total_visitor_count,
    2: i32 today_visitor_count,
}

struct Session {
    1: string username,
    2: string ip,
    3: string current_action,
    4: string nickname,
    5: double logintime,
    6: i32    id,
}

struct AuthenticationInfo {
    1: double last_login_time,
    2: string nickname,
    3: i32 id,
}

struct UserRegistration {
    1: string username,
    2: string password,
    3: string nickname,
    4: string email,
    5: string signature,
    6: string self_introduction,
    7: string default_language,
    8: string campus,
}

struct UserInformation {
    1 : string username,
    2 : string nickname,
    3 : string email,
    4 : string last_login_ip,
    5 : double last_logout_time,
    6 : string signature,
    7 : string self_introduction,
    8 : string default_language,
    9 : string campus,
    10: bool activated,
    11: i32 widget,
    12: i32 layout,
    13: i32 id,
}

struct UserPasswordInfo {
    1: string username,
    2: string current_password,
    3: string new_password,
}

struct UserModification {
    1: string nickname,
    2: string signature,
    3: string self_introduction,
    4: string default_language,
    5: string campus,
    6: i32 widget,
    7: i32 layout,
}

struct PublicUserInformation {
    1: string username,
    2: string nickname,
    3: string signature,
    4: string self_introduction,
    5: string last_login_ip,
    6: double last_logout_time,
    7: string email,
    8: string campus,
}

struct SearchUserResult {
    1: string username,
    2: string nickname,
}

struct BlacklistRequest {
    1: string blacklisted_user_username,
    2: bool block_article,
    3: bool block_message,
}

struct BlacklistInformation {
    1: string blacklisted_user_username,
    2: string blacklisted_user_nickname,
    3: double last_modified_date,
    4: double blacklisted_date,
    5: bool block_article,
    6: bool block_message,
    7: i32 id
}

struct Board {
    1: bool read_only,
    2: string board_name,
    3: string board_description,
    4: i32 id,
    5: bool hide,
    6: list<string> headings,
}

struct WrittenArticle {
    1: string title,
    2: string heading,
    3: string content
}

struct AttachDict {
    1: string filename,
    2: i32 file_id,
}

struct Article {
    1:  id_t id,
    2:  string title,
    3:  string heading,
    4:  string content,
    5:  double date,
    6:  i32 hit = 0,
    7:  i32 vote,
    8:  bool deleted = 0,
    9:  i32 root_id,
    10:  string author_username,
    11: string author_nickname,
    12: i32 author_id,
    13: bool blacklisted = 0,
    14: bool is_searchable = 1,
    15: double last_modified_date,
    16: optional i32 depth,  // Only used in the 'read' function
    17: optional string read_status,
    18: optional i32 reply_count,
    19: optional string type
    20: optional string board_name,
    21: optional list<AttachDict> attach,
    #19: optional i32 next,
    #20: optional i32 prev,
}

struct ArticleList {
    1: i32 last_page,
    2: i32 results,
    3: list<Article> hit,
    4: optional i32 current_page,
}

struct ArticleNumberList {
    1: i32 last_page,
    2: i32 results,
    3: list<i32> hit,
}

struct FileInfo {
    1:string file_path,
    2:string saved_filename,
}

struct DownloadFileInfo {
    1:string file_path,
    2:string saved_filename,
    3:string real_filename,
}

struct Message {
    1:i32 id,
    2:string from_,
    3:string from_nickname,
    4:string to,
    5:string to_nickname,
    6:string message,
    7:double sent_time,
    8:string read_status,
    9:optional bool blacklisted = 0,
}

struct MessageList {
    1:list<Message> hit,
    2:i32 last_page,
    3:i32 results,
    4:optional i32 new_message_count = 0,
}

struct ArticleSearchResult {
    1:list<Article> hit,
    2:i32 results,
    3:double search_time,
    4:i32 last_page,
}

struct SearchQuery {
    1:string query = '',
    2:string title = '',
    3:string content = '',
    4:string author_nickname = '',
    5:string author_username = '',
    6:string date = '',
}

struct Notice {
    1:i32 id,
    2:string content,
    3:double issued_date,
    4:double due_date,
    5:bool valid,
    6:i32 weight,
}

struct WrittenNotice {
    1:string content,
    2:double due_date,
    3:i32 weight,
}

struct WeatherInfo {
    1:string city,
    2:i32 current_temperature,
    3:string current_condition,
    4:string current_icon_url,
    5:string tomorrow_icon_url,
    6:string day_after_tomorrow_icon_url,
}

////////////////////////////////////////
// Section 3 : Service Definition
////////////////////////////////////////

service ARAraThriftInterface {
/// LoginManager Part Begin
    string guest_login(1:string guest_ip)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    VisitorCount total_visitor()
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    string login(1:string username, 2:string password, 3:string user_ip)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void logout(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool update_session(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    Session get_session(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    i32 get_user_id(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    string get_user_ip(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Session> get_current_online(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool is_logged_in(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool _update_monitor_status(1:string session_key, 2:string action),
/// Login Manager Part end
/// MemberManager Part Begin
    AuthenticationInfo authenticate(1:string username, 2:string password,
                                    3:string user_ip)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void register_(1:UserRegistration user_reg)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void backdoor_confirm(1:string session_key, 2:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void confirm(1:string username_to_confirm, 2:string activation_code)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool is_registered(1:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool is_registered_nickname(1:string nickname)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool is_registered_email(1:string email)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    UserInformation get_info(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_password(1:string session_key,
                           2:UserPasswordInfo user_password_info)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_password_sysop(1:string session_key,
                               2:UserPasswordInfo user_password_info)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_user(1:string session_key,
                     2:UserModification user_modification_info)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_authentication_email(1:string username,
                                       2:string new_email)
        throws (1:InternalError ouch,
                2:InvalidOperation invalid),
    PublicUserInformation query_by_username(1:string session_key,
                                            2:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    PublicUserInformation query_by_nick(1:string session_key,
                                        2:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void remove_user(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<SearchUserResult> search_user(1:string session_key,
                                 2:string search_user,
                                 3:string search_key="")
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    bool is_sysop(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void _logout_process(1:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// MemberManager Part End
/// BlacklistManager Part Begin
    void add_blacklist(1:string session_key, 2:string username,
                       3:bool block_article=1, 4:bool block_message=1)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void delete_blacklist(1:string session_key, 2:string username)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_blacklist(1:string session_key, 2:BlacklistRequest blacklist_info)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<BlacklistInformation> get_blacklist(1:string session_key) 
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<i32> get_article_blacklisted_userid_list(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// BlacklistManager Part End
/// BoardManager Part Begin
    void add_board(1:string session_key, 2:string board_name,
                   3:string board_description, 4:list<string> heading_list)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    Board get_board(1: string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    i32 get_board_id(1: string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<string> get_board_heading_list(1: string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch),
    list<Board> get_board_list()
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void add_read_only_board(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void return_read_only_board(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void hide_board(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void return_hide_board(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void delete_board(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void edit_board(1:string session_key, 2:string board_name,
                    3:string new_name, 4:string new_description)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// BoardManager Part End
/// ReadStatusManager Part Begin
    string check_stat(1:string session_key, 2:i32 no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<string> check_stats(1:string session_key, 2:list<i32> no_list)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void mark_as_read_list(1:string session_key, 2:list<i32> no_list)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void mark_as_read(1:string session_key, 2:i32 no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void mark_as_viewed(1:string session_key, 2:i32 no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void save_to_database(1:string username="")
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// ReadStatusManager Part End
/// ArticleManager Part Begin
    list<Article> get_today_best_list(1:i32 count=5)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Article> get_today_best_list_specific(1:string board_name, 2:i32 count=5)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Article> get_weekly_best_list(1:i32 count=5)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Article> get_weekly_best_list_specific(1:string board_name, 2:i32 count=5)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleList not_read_article_list(1:string session_key,
                                      2:i32 page=1,
                                      3:i32 page_length=20)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleList not_article_list(1:string session_key,
                                 2:i32 page=1,
                                 3:i32 page_length=20)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleList new_article_list(1:string session_key,
                                 2:i32 page,
                                 3:i32 page_length)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleList article_list(1:string session_key,
                             2:string board_name,
                             3:string heading_name,
                             4:i32 page=1,
                             5:i32 page_length=20,
                             6:bool include_all_headings=1)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Article> read_article(1:string session_key, 2:string board_name, 3:id_t no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Article> read_recent_article(1:string session_key, 2:string board_name)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleList article_list_below(1:string session_key,
                                   2:string board_name,
                                   3:string heading_name,
                                   4:id_t no,
                                   5:i32 page_length=20,
                                   6:bool include_all_headins=1)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void vote_article(1:string session_key, 2:string board_name,
                      3:id_t article_no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    i32 write_article(1:string session_key, 2:string board_name,
                      3:WrittenArticle article)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    i32 write_reply(1:string session_key, 2:string board_name,
                      3:id_t article_no, 4:WrittenArticle article)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    i32 modify_article(1:string session_key, 2:string board_name,
               3:id_t no, 4:WrittenArticle article)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void delete_article(1:string session_key,
                        2:string board_name,
                        3:id_t no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void destroy_article(1:string session_key,
                         2:string board_name,
                         3:id_t no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void fix_article_concurrency(1:string session_key,
                                 2:string board_name,
                                 3:id_t no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// ArticleManager Part End
/// FileManager Part Begin
    FileInfo save_file(1:string session_key,
                2:i32 article_id,
                3:string filename)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    DownloadFileInfo download_file(1:i32 article_id,
                2:i32 file_id)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    FileInfo delete_file(1:string session_key,
                2:i32 article_id,
                3:i32 file_id)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// FileManager Part End
/// MessagingManager Part Begin
    MessageList sent_list(1:string session_key,
                2:i32 page=1,
                3:i32 page_length=20)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    MessageList receive_list(1:string session_key,
                2:i32 page=1,
                3:i32 page_length=20)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void send_message_by_username(1:string session_key,
                2:string to_username,
                3:string msg)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void send_message_by_nickname(1:string session_key,
                2:string to_nickname,
                3:string message)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void send_message(1:string session_key,
                2:string to_data,
                3:string msg)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    Message read_received_message(1:string session_key,
                2:i32 msg_no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    Message read_sent_message(1:string session_key,
                2:i32 msg_no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void delete_received_message(1:string session_key,
                2:i32 msg_no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void delete_sent_message(1:string session_key,
                2:i32 msg_no)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),

/// MessagingManager Part End
/// SearchManager Part Begin
    void register_article()
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void ksearch(1:string query_text,
                2:i32 page = 1
                3:i32 page_length = 20)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    ArticleSearchResult search(1:string session_key,
                2:bool all_flag,
                3:string board_name,
                4:string heading_name,
                5:SearchQuery query_dict,
                6:i32 page = 1,
                7:i32 page_length = 20,
                8:bool include_all_headings = 1)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// SearchManager Part End
/// NoticeManager Part Begin
    string get_banner()
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    string get_welcome()
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Notice> list_banner(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    list<Notice> list_welcome(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void add_banner(1:string session_key,
                    2:WrittenNotice notice_reg_dic)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void add_welcome(1:string session_key,
                    2:WrittenNotice notice_reg_dic)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void modify_banner_validity(1:string session_key,
                                2:i32 id, 3:bool valid)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void remove_banner(1:string session_key,
                    2:i32 id)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    void remove_welcome(1:string session_key,
                    2:i32 id)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// NoticeManager Part End
/// BotManager Part Start
    void refresh_weather_info(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
    WeatherInfo get_weather_info(1:string session_key)
        throws (1:InvalidOperation invalid,
                2:InternalError ouch, 3:NotLoggedIn not_logged_in),
/// BotManager Part End
}
