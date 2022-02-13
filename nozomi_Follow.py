#############################
# Parameter
#############################
spd = 'Slow'

#############################
# Data
#############################
import tweepy
import time

my_user_name = 'Nozomi'

# Get API_KEY
import os
API_KEY = os.environ[my_user_name + '_API_KEY']
API_SECRET = os.environ[my_user_name + '_API_SECRET']
ACCESS_TOKEN = API_SECRET = os.environ[my_user_name + '_ACCESS_TOKEN']
ACCESS_SECRET = API_SECRET = os.environ[my_user_name + '_ACCESS_SECRET']

# Get user status
my_user_id = os.environ[my_user_name + '_user_id']
shiratama_id = os.environ['shiratama_id']
AutoFollow_Keyword = os.environ['AutoFollow_Keyword']

if spd == 'Fast':
    get_tweet_cnt = 70    # amount getting tweets / 1 hour
    follow_cnt = 36        # amount folloing / 1 hour
elif spd == 'Slow':
    get_tweet_cnt = 30    # amount getting tweets / 1 hour
    follow_cnt = 12        # amount folloing / 1 hour
else:  #Normal
    get_tweet_cnt = 50    # amount getting tweets / 1 hour
    follow_cnt = 24        # amount folloing / 1 hour

#############################
#  Method
#############################
def NG_USER_CHECK(user_description):
    NG_keywords = os.environ[NG_keywords]
    hit_NGword =""
    for keyword in NG_keywords:
        if keyword in user_description:
            hit_NGword = keyword
            return hit_NGword
    return ""

def GET_FOLLOWBACK_TWEETS(api, cnt):
    import random

    i = random.randint(0,4)
    word = AutoFollow_Keyword[i]
    
    tweets = api.search_tweets(q=word, result_type='recent', count=cnt)
    return tweets


def AUTO_FOLLOW_v2(api, tweets, my_user_id, my_user_name, speed, follow_cnt):
    cnt = 0
    PGname = 'AutoFollow.py'
    follow_result = 0
    
    # Default
    wait_time= 150

    if speed == 'Fast':
        wait_time = 100

    elif speed == 'Slow':
        wait_time = 300

    for a_tweet in tweets:
        try:
            this_tweet_id = a_tweet.retweeted_status.id
            this_user_id = a_tweet.retweeted_status.author.id
            this_user_name = a_tweet.retweeted_status.author.name
            this_user_screen_name = a_tweet.retweeted_status.author.screen_name
            this_user_description = a_tweet.retweeted_status.author.description
        except Exception as e:
            this_tweet_id = a_tweet.id
            this_user_id = a_tweet.user._json['id']
            this_user_name = a_tweet.user._json['name']
            this_user_screen_name = a_tweet.user._json['screen_name']
            this_user_description = a_tweet.user._json['description']
        else:
            
            # 自分と相手，お互いのフォロー状況を抽出（tuple[0]は自分の情報，tuple[1]は相手の情報）
            our_friendship = api.get_friendship(source_id=my_user_id,target_id=this_user_id)

            # NG word check in description
            if "" != NG_USER_CHECK(this_user_description):
                continue

            if our_friendship[0]._json['following'] == False:  #まだフォローしていない場合は，フォロー\nする
                try:
                    api.create_friendship(user_id=this_user_id) # 友達申請
                    follow_result = follow_result + 1
                except Exception as e:
                    message = "友達申請に失敗しました。"
#                   LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, target_user_id=this_user_id, target_user_name=this_user_name,target_user_screen_name=this_user_screen_name, info_level="FAILED",tweet_id=this_tweet_id, message=message, action="FOLLOW")
                else:
                    cnt = cnt + 1
#                   LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, target_user_id=this_user_id, target_user_name=this_user_name,target_user_screen_name=this_user_screen_name,info_level="SUCCESS",tweet_id=this_tweet_id, action="FOLLOW")
                
                # Execute Retweet
                try:
                    api.retweet(this_tweet_id) 
                except Exception as e:
                    # 既にリツイートしている記事の時も，エラーになる。
                    message = "リツイートに失敗しました。"
#                   LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, target_user_id=this_user_id, target_user_name=this_user_name, target_user_screen_name=this_user_screen_name,info_level="FAILED", message=message, action="RETWEET")
                    continue
                else:
                    # 改行を削除
                    campaign_tweet_contents = a_tweet._json['text']
                    campaign_tweet_contents= campaign_tweet_contents.replace( '\n' , '' )
                    # write
#                   LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, target_user_id=this_user_id, target_user_name=this_user_name, target_user_screen_name=this_user_screen_name, tweet_id=this_tweet_id, tweet_contents=campaign_tweet_contents ,info_level="SUCCESS", action="RETWEET")
                    
                    # 必要数のフォローが完了した場合，プログラムを強制終了する。
                    if follow_cnt == cnt:
#                       LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, info_level="INFO", follow_cnt=cnt)
                        return
                    # フォローに成功したら一定時間まつ，過負荷はアカウント凍結の恐れがあるため。
                    time.sleep(wait_time)
    
#    LOG_OUTPUT(PGname=PGname, my_user_name=my_user_name, info_level="INFO", follow_cnt=cnt)
    return follow_result


# API Connection
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit = True)

for n in range(5):
    if 0 < follow_cnt:
        # Get user timeline
        # Get tweet
        tweets = GET_FOLLOWBACK_TWEETS(api, cnt=get_tweet_cnt)

        # Auto Follow
        follow_cnt = follow_cnt - AUTO_FOLLOW_v2(api, tweets, my_user_id, my_user_name, spd, follow_cnt)
